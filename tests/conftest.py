import json

import pytest
from jikken.database.config import JikkenConfig
from jikken.utils import check_mongo
from jikken.database import DataBase



TEST_CONFIG_JSON = {
    "input_parameters": {
        "filepath": "/data",
        "preprocessing": True,
        "batch_size": 4,
        "transformations": [
            "stopwords",
            "tokenize",
            "remove_punct"
        ]
    },
    "training_parameters": {
        "algorithm": "Seq2Seq",
        "batch_size": 100,
        "attention": "multiplicative"
    }
}

TEST_SCRIPT = \
    """
   import click
   import json
   @click.command()
   @click.argument('configuration_path', type=click.Path(exists=True, file_okay=True, dir_okay=True))
   @click.argument('input_path',required=False ,type=click.Path(exists=True, file_okay=True, dir_okay=True))
   @click.argument('output_path',required=False ,type=click.Path(exists=True, file_okay=True, dir_okay=True))
   @click.option('--var1',default=None)
   @click.option('--var2', default=None)
   def main(configuration_path,input_path, output_path,var1,var2):
       print(open(configuration_path).readlines())
       if var1 is not None:
           print("var1=",var1)
       if var2 is not None:
           print("var2=",var2) 
   if __name__ == '__main__':
       main()
   """


@pytest.fixture()
def file_setup(tmpdir):
    conf_file = tmpdir.join('configuration.json')
    conf_file.write(json.dumps(TEST_CONFIG_JSON))

    script_file = tmpdir.join('script.py')
    code = "\n".join([line[3:] for line in TEST_SCRIPT.split("\n")])
    script_file.write(code)
    return conf_file.strpath, script_file.strpath, TEST_CONFIG_JSON


database_types = ("tiny",
                  "mongo"
                  )


@pytest.fixture(params=database_types)
def db_config(tmpdir, request):
    if request.param == 'tiny':
        db_path = str(tmpdir.mkdir("temp"))
    elif request.param == 'mongo':

        db_path = "mongodb://localhost:27019"
        if not check_mongo(uri=db_path):
            pytest.skip("mongo db not available")
    return JikkenConfig(db_path=db_path, db_type=request.param)


@pytest.fixture()
def jikken_db_session(db_config, mocker):
    """Connect to db before tests, disconnect after."""
    test_database = DataBase(config=db_config)
    yield test_database
    test_database.stop_db()
    del test_database


@pytest.fixture()
def jikken_db(jikken_db_session):
    yield jikken_db_session
    jikken_db_session.delete_all()
    del jikken_db_session
