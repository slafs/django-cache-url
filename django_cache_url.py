# -*- coding: utf-8 -*-

import os

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


# Register cache schemes in URLs.
urlparse.uses_netloc.append('db')
urlparse.uses_netloc.append('dummy')
urlparse.uses_netloc.append('file')
urlparse.uses_netloc.append('locmem')
urlparse.uses_netloc.append('memcached')
urlparse.uses_netloc.append('djangopylibmc')
urlparse.uses_netloc.append('pymemcached')
urlparse.uses_netloc.append('redis')
urlparse.uses_netloc.append('hiredis')
urlparse.uses_netloc.append('djredis')
urlparse.uses_netloc.append('djredisunix')
urlparse.uses_netloc.append('djrediss')
urlparse.uses_netloc.append('djhiredis')
urlparse.uses_netloc.append('djhiredisunix')
urlparse.uses_netloc.append('djhirediss')

DEFAULT_ENV = 'CACHE_URL'

CACHE_TYPES = {
    'db': 'django.core.cache.backends.db.DatabaseCache',
    'dummy': 'django.core.cache.backends.dummy.DummyCache',
    'file': 'django.core.cache.backends.filebased.FileBasedCache',
    'locmem': 'django.core.cache.backends.locmem.LocMemCache',
    'memcached': 'django.core.cache.backends.memcached.PyLibMCCache',
    'djangopylibmc': 'django_pylibmc.memcached.PyLibMCCache',
    'pymemcached': 'django.core.cache.backends.memcached.MemcachedCache',
    'redis': 'redis_cache.cache.RedisCache',
    'hiredis': 'redis_cache.cache.RedisCache',
    'djredis': 'django_redis.cache.RedisCache',
    'djrediss': 'django_redis.cache.RedisCache',
    'djhiredis': 'django_redis.cache.RedisCache',
    'djhirediss': 'django_redis.cache.RedisCache',
    'djredisunix': 'django_redis.cache.RedisCache',
    'djhiredisunix': 'django_redis.cache.RedisCache',
}


def config(env=DEFAULT_ENV, default='locmem://'):
    """Returns configured CACHES dictionary from CACHE_URL"""
    config = {}

    s = os.environ.get(env, default)

    if s:
        config = parse(s)

    return config


def parse(url):
    """Parses a cache URL."""
    config = {}

    url = urlparse.urlparse(url)
    # Update with environment configuration.
    config['BACKEND'] = CACHE_TYPES[url.scheme]
    if url.scheme == 'file':
        config['LOCATION'] = url.path
        return config

    elif url.scheme in ('djredis', 'djrediss', 'djhiredis', 'djhirediss', 'djredisunix', 'djhiredisunix'):

        options = {}
        hiredis = False
        db = None
        prefix = ''
        netloc = url.netloc or '@'
        path = url.path

        # get db and prefix
        query = urlparse.parse_qs(url.query)
        if query:
            db = query.get('db', ['0'])[0]
            prefix = query.get('prefix', [''])[0]

        # get resulting scheme
        new_scheme = url.scheme[2:]  # drop dj
        if new_scheme.startswith('hi'):
            new_scheme = new_scheme[2:]
            hiredis = True

        if 'unix' in url.scheme:
            new_scheme = 'unix'
        else:
            if path:
                # an alternative way to specify db and prefix in path
                db_prefix = path.split('/', 2)
                db = db_prefix[1]
                if not db:
                    db = None
                if len(db_prefix) == 3:
                    prefix = db_prefix[2]
                path = ''

        config['KEY_PREFIX'] = prefix

        if hiredis:
            options['PARSER_CLASS'] = 'redis.connection.HiredisParser'
            config['OPTIONS'] = options

        db_qs = ('db=' + db) if db else ''

        new_url = urlparse.ParseResult(scheme=new_scheme, netloc=netloc,
                                       path=path, params='', query=db_qs,
                                       fragment='')
        config['LOCATION'] = new_url.geturl()

    elif url.scheme in ('redis', 'hiredis'):
        if url.netloc == 'unix':
            location_index = None
            bits = list(filter(None, url.path.split('/')))
            # find the end of the socket path
            for index, bit in enumerate(bits, 1):
                if bit.endswith(('.sock', '.socket')):
                    location_index = index
                    break

            if location_index is None:
                # no socket file extension found, using the whole location
                location = bits
            else:
                # splitting socket path from database and prefix
                location = bits[:location_index]
                rest = bits[location_index:]
                if len(rest) > 0:
                    try:
                        # check if first item of the rest is a database
                        database = int(rest[0])
                        prefix = rest[1:]
                    except ValueError:
                        # or assume the rest is the prefix
                        database = 0
                        prefix = rest
                else:
                    database = prefix = None

            full_location = (url.netloc, '/' + '/'.join(location))
            if database is not None:
                full_location += (str(database),)
            config['LOCATION'] = ':'.join(full_location)
            config['KEY_PREFIX'] = '/'.join(prefix)

        else:
            try:
                userpass, hostport = url.netloc.split('@')
            except ValueError:
                userpass, hostport = '', url.netloc

            try:
                username, password = userpass.split(':')
            except ValueError:
                pass

            path = list(filter(None, url.path.split('/')))
            config['LOCATION'] = ':'.join((hostport, path[0]))
            config['KEY_PREFIX'] = '/'.join(path[1:])

        redis_options = {}

        if url.scheme == 'hiredis':
            redis_options['PARSER_CLASS'] = 'redis.connection.HiredisParser'

        try:
            if password:
                redis_options['PASSWORD'] = password
        except NameError:  # No password defined
            pass

        if redis_options:
            config['OPTIONS'] = redis_options

    else:
        netloc_list = url.netloc.split(',')
        if len(netloc_list) > 1:
            config['LOCATION'] = netloc_list
        else:
            config['LOCATION'] = url.netloc
        config['KEY_PREFIX'] = url.path[1:]

    return config
