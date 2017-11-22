from functools import singledispatch


def map_multistage(multistage):
    return multistage


def map_experiment(experiment: dict):
    new_experiment = {}
    for key in experiment['variables'].keys():
        new_key = key.replace(".", "__")
        new_experiment[new_key] = experiment['variables'][key]
    experiment['variables'] = new_experiment
    experiment['stdout'] = []
    experiment['stderr'] = []
    return experiment


def inv_map_experiment(experiment: dict):
    new_experiment = {}
    for key in experiment['variables'].keys():
        new_key = key.replace("__", ".")
        new_experiment[new_key] = experiment['variables'][key]
    experiment['variables'] = new_experiment
    experiment['id'] = str(experiment.pop("_id"))
    experiment['stdout'] = "".join([line for line in experiment['stdout']])
    experiment['stderr'] = "".join([line for line in experiment['stderr']])
    return experiment


@singledispatch
def add_mongo(value, *, key):
    if isinstance(key, list):
        key = ".".join(key)
    return {"$addToSet": {key: value}}


@add_mongo.register(str)
def _(text, *, key):
    if isinstance(key, list):
        key = ".".join(key)
    return {"$push": {key: text}}


@add_mongo.register(int)
def _(number, *, key):
    if isinstance(key, list):
        key = ".".join(key)
    return {"$inc": {key: number}}


@add_mongo.register(set)
@add_mongo.register(list)
def _(value, *, key):
    if isinstance(key, list):
        key = ".".join(key)
    return {"$addToSet": {key: value}}


def set_mongo(value, *, key):
    # value = [value] if key in ["stdout", "stderr"] else value
    if isinstance(key, list):
        key = ".".join(key)
    return {"$set": {key: value}}


def add_inner(fields, n):
    """
    Add n to a given field in the document.
    """

    def transform(doc):
        for field in fields[:-1]:
            ref = doc[field]
        ref[fields[-1]] += n

    return transform


def set_inner(fields, n):
    """
    Set n from a given field in the document.
    """

    def transform(doc):
        for field in fields[:-1]:
            ref = doc[field]
        ref[fields[-1]] = n

    return transform


def map_es_experiment(experiment: dict, doc_type="experiment"):
    if doc_type == "experiment":
        experiment['stdout'] = []
        experiment['stderr'] = []
    return experiment


def inv_map_es_experiment(experiment: dict, doc_type="experiment"):
    _id = experiment["_id"]
    experiment = experiment['_source']
    experiment['id'] = str(_id)
    if doc_type == 'experiment':
        experiment['stdout'] = "".join([line for line in experiment['stdout']])
        experiment['stderr'] = "".join([line for line in experiment['stderr']])
    return experiment
