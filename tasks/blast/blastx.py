import luigi
from luigi.mock import MockTarget
import os
import time
import subprocess
import json
from tasks.blast.make_blast_db import MakeBlastDb


class Blastx(luigi.Task):
    task_namespace = 'blast'
    working_dir = luigi.Parameter()
    parameter_str = luigi.Parameter()

    def requires(self):
        input_parameter = json.loads(self.parameter_str)
        return MakeBlastDb(working_dir=self.working_dir,
                          blast_home=input_parameter['blast_home'],
                          input_path=input_parameter['database']['path'],
                          dbtype=input_parameter['database']['dbtype'],
                          options=input_parameter['makeblastdb_options'])

    def get_working_dir_path(self):
        return os.path.join(self.working_dir,
                            self.task_namespace,
                            self.__class__.__name__,
                            self.task_id)

    def run(self):
        with self.input().open('r') as input_file:
            make_blast_db_result = json.load(input_file)

        working_dir = self.get_working_dir_path()
        print('task_id: ', self.task_id)
        input_parameter=json.loads(self.parameter_str)
        parameter = {
            'blast_home': os.path.abspath(input_parameter['blast_home']),
            'working_dir': os.path.abspath(working_dir),
            'query_path': os.path.abspath(input_parameter['query']['path']),
            'db_path': os.path.abspath(make_blast_db_result['parameter']['output_path']),
            'options': input_parameter['blastx_options'],
        }
        print('parameters: ')
        print(json.dumps(parameter, indent=4))

        result = {
            'parameter': parameter,
        }

        os.makedirs(working_dir, exist_ok=True)
        script_file_name = 'run.sh'
        script_path = os.path.join(working_dir, script_file_name)
        self.build_script(script_path, parameter)
        elapsed_time, log = self.run_script(working_dir, script_file_name)
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
        result['elapsed_time'] = elapsed_time
        with open(os.path.join(working_dir, 'log.out'), 'w') as f:
            f.write(log)
        result['log'] = log
        self.run_script(working_dir, script_file_name)

        with self.output().open('w') as output:
            json.dump(result, output, indent=4)

    def output(self):
        #return MockTarget('result.json')
        working_dir = self.get_working_dir_path()
        return luigi.LocalTarget(os.path.join(working_dir, 'result.json'))

    def build_script(self, path, parameter):
        with open(path, 'w') as f:
            f.write('''#!/bin/sh
{blast_home}/bin/blastx -query {query_path} -db {db_path} {options}
'''.format(**parameter))

    def run_script(self, working_dir, script_file_name):
        shell_commands = [
            'sh ./{script_file_name}'.format(script_file_name=script_file_name),
        ]
        start = time.time()
        log = subprocess.check_output('sh -cx "{0}"'.format(' && '.join(shell_commands)), cwd=working_dir, shell=True)
        elapsed_time = time.time() - start
        log = log.decode('unicode_escape')
        return elapsed_time, log