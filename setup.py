from setuptools import setup, find_packages

setup(
        name='duckysearch',
        packages=find_packages(),
        entry_points={
            'duckysearch.indexer': [
                'localfs = duckysearch.indexers.localfs.localfs:Localfs',
                'mountedcifs = duckysearch.indexers.mountedcifs.mountedcifs:Mountedcifs',
                ]
            }
        )