# class for logging experiments


import numpy as np
import sys
import os
import socket
import json
import yaml
from tinydb import TinyDB
from tinydb.storages import JSONStorage
import omegaconf
from tinydb.table import Document
import torch
from datetime import datetime
from random import random
from time import sleep
import dill as pkl
import shutil
import pprint
class Logger(object):
    def __init__(self, config, overwrite=None):
        #self.git_store_commit()

        #self.device = assign_device(self.config.device)
        print(f"Process id: {str(os.getpid())} | hostname: {socket.gethostname()}")
        print(f"Time: {datetime.now()}")
        self.pp = pprint.PrettyPrinter(indent=4)
        self.pp.pprint(vars(config))

        self.config = config
        self.root = os.path.join(os.path.abspath(self.config.logs.log_dir), self.config.logs.log_name)
        self.db_run_id = config.logs.log_id

        self.setup_dir()
        self.update_run_config()
        self.log_file()
        self.log_config()
        #set_seeds(self.config.system.seed)
        
    def get_log_dir(self):
        return self.db_run_id,self.dir

    def setup_dir(self):
        os.makedirs(self.root, exist_ok=True)
        self.db_run_id, self.dir = _make_run_dir(self.db_run_id, self.root)
        #mlflow.set_tracking_uri("file:/"+self.root )

    def update_run_config(self):
        now = datetime.now()
        date = now.strftime("%d/%m/%Y")
        time = now.strftime("%H:%M:%S")       
        omegaconf.OmegaConf.set_struct(self.config, True)
        with omegaconf.open_dict(self.config):
            self.config.system.hostname = socket.gethostname()
            self.config.system.process_id = os.getpid()
            self.config.logs.log_id = self.db_run_id
            self.config.logs.path = os.path.join(self.root,str(self.db_run_id))
            self.config.system.date= date
            self.config.system.time=time

    def log_config(self):
        _log_config(self.config,"metadata",self.dir)



    def log_metrics(self,metrics_dict, tag='', step=None):
        #mlflow.log_metics(metrics_dict, step=step)
        file_name = os.path.join(self.dir, tag+f'metrics')
        with open(file_name+'.json','a') as f:
            json.dump(metrics_dict,f)
            f.write(os.linesep)

    def log_artifacts(self,artifact, step, art_type, tag='',copy=False,copy_tag=''):
        subdir= os.path.join(self.dir, art_type)
        os.makedirs(subdir, exist_ok=True)
        fname = os.path.join(subdir, f'{tag}_{str(step)}')
        if art_type=='arrays':
            np.savez(fname, **artifact)
        elif art_type=='figures':
            artifact.savefig(f'{fname}.png',bbox_inches='tight')
        elif art_type=='torch_models':
            torch.save(artifact, f'{fname}.pth')
            print('Model saved at ' + fname+'.pth')
        elif art_type=='checkpoints':
            with open(f'{fname}.pkl', 'wb') as f:
                pkl.dump(artifact, f)
            if copy:
                copy_fname = os.path.join(subdir, f'{copy_tag}_{str(step)}')
                shutil.copy(f'{fname}.pkl', f'{copy_fname}.pkl')

    def log_file(self):
        if self.config.logs.log_to_file:
            log_file = open(os.path.join(self.dir, f'log.txt'), 'w', buffering=1)
            sys.stdout = log_file
            sys.stderr = log_file


def config_to_dict(config):
    done = False
    out_dict = {}
    for key, value in config.items():
        if isinstance(value,omegaconf.dictconfig.DictConfig):
            out_dict[key] =  config_to_dict(value)
        else:
            out_dict[key] = value
    return out_dict


def _make_run_dir(_id, root):
    os.makedirs(root, exist_ok=True)
    log_dir = None
    if _id is None:
        fail_count = 0
        #_id = self._maximum_existing_run_id() + 1
        while log_dir is None:
            try:
                _id = _maximum_existing_run_id(root) + 1
                log_dir = _make_dir(_id, root)
            except FileExistsError:  # Catch race conditions
                sleep(random())
                if fail_count < 1000:
                    fail_count += 1
                else:  # expect that something else went wrong
                    raise
    else:
        log_dir = os.path.join(root, str(_id))
        os.makedirs(root, exist_ok=True)
    return _id, log_dir
def _maximum_existing_run_id(root):
    dir_nrs = [
        int(d)
        for d in os.listdir(root)
        if os.path.isdir(os.path.join(root, d)) and d.isdigit()
    ]
    if dir_nrs:
        return max(dir_nrs)
    else:
        return 0
def _make_dir( _id, root):
    log_dir = os.path.join(root, str(_id))
    os.mkdir(log_dir)
    return log_dir  # set only if mkdir is successful


def _log_config(cfg, file_name, path):
    # config contains only experiment parameters
    # host_info:  slurm id, hostname, gpu , etc
    # meta : run_id, starting time, slum id
    abs_name= os.path.join(path, file_name)

    #config_dict = config_to_dict(cfg)
    #config_dict = set_date_time(config_dict)

    # with TinyDB(abs_name+".json", storage=JSONStorage) as db: 
    #     runs = db.table("runs")
    #     runs.upsert(Document(config_dict, doc_id=self.db_run_id ) )
    #for key, value in config_dict.items():
    #    mlflow.log_param(key, value)
    omegaconf.OmegaConf.save(config=cfg, f=abs_name+".yaml")
    # yaml_cfg = omegaconf.OmegaConf.to_yaml(cfg)
    # with open(abs_name+".yaml", 'w') as file: 
    #     documents = yaml.dump(yaml_cfg, file) 
    #     print(document)

def set_date_time(config_dict):
    now = datetime.now()
    date = now.strftime("%d/%m/%Y")
    time = now.strftime("%H:%M:%S")
    if config_dict['system']['date']=='' or config_dict['system']['time']=='':
        config_dict['system']['date'] = date
        config_dict['system']['time'] = time


