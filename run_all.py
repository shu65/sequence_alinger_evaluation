import luigi
from tasks import blast
from tasks import diamond
import yaml
import json
from luigi.mock import MockTarget

class Main(luigi.Task):
    working_dir = luigi.Parameter()
    parameter_path = luigi.Parameter()

    def requires(self):
        with open(self.parameter_path) as f:
            parameter = yaml.load(f)
        print(json.dumps(parameter, indent=2))
        return [blast.Main(working_dir=self.working_dir, parameter_str=json.dumps(parameter['blast'])),
                diamond.Main(working_dir=self.working_dir, parameter_str=json.dumps(parameter['diamond'])),
                ]

    def run(self):
        with self.output().open('w') as output:
            output.write("done")

    def output(self):
        return MockTarget('result.json')


if __name__ == '__main__':
    luigi.run(['Main', '--workers', '1', '--local-scheduler'])