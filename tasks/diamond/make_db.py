import luigi
from luigi.mock import MockTarget
import os
import time
import subprocess
import json


class MakeDb(luigi.Task):
    task_namespace = 'diamond'
    working_dir = luigi.Parameter()
    diamond_home=luigi.Parameter()
    input_path = luigi.Parameter()
    options = luigi.Parameter()

    def requires(self):
        pass

    def get_working_dir_path(self):
        return os.path.join(self.working_dir,
                     self.task_namespace,
                     self.__class__.__name__,
                     self.task_id)

    def run(self):
        working_dir = self.get_working_dir_path()
        print('task_id: ', self.task_id)

        parameter = {
            'diamond_home': os.path.abspath(self.diamond_home),
            'working_dir': os.path.abspath(working_dir),
            'input_path':  os.path.abspath(self.input_path),
            'output_path': os.path.join(os.path.abspath(working_dir), 'database', os.path.basename(str(self.input_path))),
            'options': self.options
        }
        print('parameters: ')
        print(json.dumps(parameter, indent=4))

        result = {
            'parameter':parameter,
        }

        os.makedirs(working_dir, exist_ok=True)
        os.makedirs(os.path.dirname(parameter['output_path']), exist_ok=True)
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
{diamond_home}/diamond makedb --in {input_path} -d {output_path} {options}
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






