import luigi
from luigi.mock import MockTarget
from tasks.blast.blastx import Blastx
from sklearn.model_selection import ParameterGrid
import json
import os


class Main(luigi.Task):
    task_namespace = 'blast'
    working_dir = luigi.Parameter()
    parameter_str = luigi.DictParameter()

    def requires(self):
        parameters = list(ParameterGrid(json.loads(self.parameter_str)))
        for parameter in parameters:
            yield Blastx(working_dir=self.working_dir, parameter_str=json.dumps(parameter))


    def run(self):
        with self.output().open('w') as output:
            output.write("done")

    def output(self):
        return MockTarget('log')
        #return luigi.LocalTarget(os.path.join(self.working_dir, 'done.out'))
