from os import environ
from unittest import TestCase

from nose.tools import assert_equals
try:
    from nose.tools import assert_in
except ImportError:
    # Pre-Python 2.7
    def assert_in(val, elems): assert val in elems, "%r not found in %r" % (val, elems)

import django_cache_url


class Base(TestCase):
    def setUp(self):
        try:
            del environ['CACHE_URL']  # make sure
        except KeyError:
            pass


class TestConfigOptions(Base):
    location = 'django.core.cache.backends.memcached.PyLibMCCache'

    def test_setting_default_var(self):
        config = django_cache_url.config(default='memcached://127.0.0.1:11211')
        assert_equals(config['BACKEND'], self.location)
        assert_equals(config['LOCATION'], '127.0.0.1:11211')

    def test_setting_env_var_name(self):
        environ['HERP'] = 'memcached://127.0.0.1:11211'
        config = django_cache_url.config(env='HERP')
        assert_equals(config['BACKEND'], self.location)
        assert_equals(config['LOCATION'], '127.0.0.1:11211')


class TestDatabaseCache(Base):
    def setUp(self):
        super(TestDatabaseCache, self).setUp()
        environ['CACHE_URL'] = 'db://super_caching_table'

    def test_db_url_returns_database_cache(self):
        location = 'django.core.cache.backends.db.DatabaseCache'
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], location)

    def test_db_url_returns_location_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], 'super_caching_table')


class TestDummyCache(Base):
    def test_dummy_url_returns_dummy_cache(self):
        environ['CACHE_URL'] = 'dummy://'
        location = 'django.core.cache.backends.dummy.DummyCache'
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], location)


class TestFileCache(Base):
    def setUp(self):
        super(TestFileCache, self).setUp()
        environ['CACHE_URL'] = 'file:///herp'

    def test_file_url_returns_file_cache_backend(self):
        location = 'django.core.cache.backends.filebased.FileBasedCache'
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], location)

    def test_file_url_returns_location_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], '/herp')


class TestLocMemCache(Base):
    location = 'django.core.cache.backends.locmem.LocMemCache'

    def test_config_defaults_to_locmem(self):
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], self.location)

    def test_locmem_url_returns_locmem_cache(self):
        environ['CACHE_URl'] = 'locmem://'
        config = django_cache_url.config('')
        assert_equals(config['BACKEND'], self.location)


class TestMemcachedCache(Base):
    def setUp(self):
        super(TestMemcachedCache, self).setUp()
        environ['CACHE_URL'] = 'memcached://127.0.0.1:11211/prefix'

    def test_memcached_url_returns_pylibmc_cache(self):
        location = 'django.core.cache.backends.memcached.PyLibMCCache'
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], location)

    def test_memcached_url_returns_location_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], '127.0.0.1:11211')

    def test_memcached_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], 'prefix')

    def test_memcached_url_multiple_locations(self):
        environ['CACHE_URL'] = 'memcached://127.0.0.1:11211,192.168.0.100:11211/prefix'
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], ['127.0.0.1:11211', '192.168.0.100:11211'])


class TestRedisCache(Base):
    def setUp(self):
        super(TestRedisCache, self).setUp()
        environ['CACHE_URL'] = 'redis://127.0.0.1:6379/0/prefix'

    def test_redis_url_returns_redis_cache(self):
        location = 'redis_cache.cache.RedisCache'
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], location)

    def test_redis_url_returns_location_and_port_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], '127.0.0.1:6379:0')

    def test_redis_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], 'prefix')


class TestHiredisCache(Base):
    def setUp(self):
        super(TestHiredisCache, self).setUp()
        environ['CACHE_URL'] = 'hiredis://127.0.0.1:6379/0/prefix'

    def test_hiredis_url_returns_redis_cache(self):
        location = 'redis_cache.cache.RedisCache'
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], location)

    def test_hiredis_url_returns_location_and_port_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], '127.0.0.1:6379:0')

    def test_hiredis_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], 'prefix')

    def test_hiredis_url_sets_hiredis_parser(self):
        config = django_cache_url.config()
        assert_equals(config['OPTIONS']['PARSER_CLASS'],
                      'redis.connection.HiredisParser')


class TestRedisCacheWithPassword(Base):
    def setUp(self):
        super(TestRedisCacheWithPassword, self).setUp()
        environ['CACHE_URL'] = 'redis://:redispass@127.0.0.1:6379/0/prefix'

    def test_redis_url_returns_redis_cache(self):
        location = 'redis_cache.cache.RedisCache'
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], location)

    def test_redis_url_returns_location_and_port_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], '127.0.0.1:6379:0')

    def test_redis_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], 'prefix')

    def test_redis_url_returns_password(self):
        config = django_cache_url.config()
        assert_in('OPTIONS', config)
        assert_in('PASSWORD', config['OPTIONS'])
        assert_equals(config['OPTIONS']['PASSWORD'], 'redispass')


class TestRedisBothSocketCache(Base):
    def setUp(self):
        super(TestRedisBothSocketCache, self).setUp()
        environ['CACHE_URL'] = 'redis://unix/path/to/socket/file.sock/1/prefix'

    def test_socket_url_returns_redis_cache(self):
        location = 'redis_cache.cache.RedisCache'
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], location)

    def test_socket_url_returns_location_and_port_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], 'unix:/path/to/socket/file.sock:1')

    def test_socket_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], 'prefix')


class TestRedisDatabaseSocketCache(TestRedisBothSocketCache):
    def setUp(self):
        super(TestRedisDatabaseSocketCache, self).setUp()
        environ['CACHE_URL'] = 'redis://unix/path/to/socket/file.sock/1'

    def test_socket_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], '')


class TestRedisPrefixSocketCache(TestRedisBothSocketCache):
    def setUp(self):
        super(TestRedisPrefixSocketCache, self).setUp()
        environ['CACHE_URL'] = 'redis://unix/path/to/socket/file.sock/prefix'

    def test_socket_url_returns_location_and_port_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], 'unix:/path/to/socket/file.sock:0')

    def test_socket_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], 'prefix')


class TestHiredisDatabaseSocketCache(TestRedisDatabaseSocketCache):
    def setUp(self):
        super(TestHiredisDatabaseSocketCache, self).setUp()
        environ['CACHE_URL'] = 'hiredis://unix/path/to/socket/file.sock/1'

    def test_hiredis_url_sets_hiredis_parser(self):
        config = django_cache_url.config()
        assert_equals(config['OPTIONS']['PARSER_CLASS'],
                      'redis.connection.HiredisParser')


class TestHiredisPrefixSocketCache(TestRedisPrefixSocketCache):
    def setUp(self):
        super(TestHiredisPrefixSocketCache, self).setUp()
        environ['CACHE_URL'] = 'hiredis://unix/path/to/socket/file.sock/prefix'

    def test_hiredis_url_sets_hiredis_parser(self):
        config = django_cache_url.config()
        assert_equals(config['OPTIONS']['PARSER_CLASS'],
                      'redis.connection.HiredisParser')


class TestDjRedisCache(Base):
    def setUp(self):
        super(TestDjRedisCache, self).setUp()
        environ['CACHE_URL'] = 'djredis://127.0.0.1:6379/0/prefix'

    def test_redis_url_returns_redis_cache(self):
        location = 'django_redis.cache.RedisCache'
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], location)

    def test_redis_url_returns_location_and_port_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], 'redis://127.0.0.1:6379?db=0')

    def test_redis_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], 'prefix')


class TestDjRedisSSLCache(Base):
    def setUp(self):
        super(TestDjRedisSSLCache, self).setUp()
        environ['CACHE_URL'] = 'djrediss://127.0.0.1:6379/0/prefix'

    def test_redis_url_returns_redis_cache(self):
        location = 'django_redis.cache.RedisCache'
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], location)

    def test_redis_url_returns_location_and_port_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], 'rediss://127.0.0.1:6379?db=0')

    def test_redis_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], 'prefix')


class TestDjHiRedisCache(Base):
    def setUp(self):
        super(TestDjHiRedisCache, self).setUp()
        environ['CACHE_URL'] = 'djhiredis://127.0.0.1:6379/0/prefix'

    def test_redis_url_returns_redis_cache(self):
        location = 'django_redis.cache.RedisCache'
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], location)

    def test_redis_url_returns_location_and_port_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], 'redis://127.0.0.1:6379?db=0')

    def test_redis_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], 'prefix')

    def test_hiredis_url_sets_hiredis_parser(self):
        config = django_cache_url.config()
        assert_equals(config['OPTIONS']['PARSER_CLASS'],
                      'redis.connection.HiredisParser')


class TestDjHiRedisSSLCache(Base):
    def setUp(self):
        super(TestDjHiRedisSSLCache, self).setUp()
        environ['CACHE_URL'] = 'djhirediss://127.0.0.1:6379/0/prefix'

    def test_redis_url_returns_redis_cache(self):
        location = 'django_redis.cache.RedisCache'
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], location)

    def test_redis_url_returns_location_and_port_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], 'rediss://127.0.0.1:6379?db=0')

    def test_redis_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], 'prefix')

    def test_hiredis_url_sets_hiredis_parser(self):
        config = django_cache_url.config()
        assert_equals(config['OPTIONS']['PARSER_CLASS'],
                      'redis.connection.HiredisParser')


class TestDjRedisBothSocketCache(Base):
    def setUp(self):
        super(TestDjRedisBothSocketCache, self).setUp()
        environ['CACHE_URL'] = 'djredisunix:///path/to/socket/file.sock?db=1&prefix=prefix'

    def test_socket_url_returns_redis_cache(self):
        location = 'django_redis.cache.RedisCache'
        config = django_cache_url.config()
        assert_equals(config['BACKEND'], location)

    def test_socket_url_returns_location_and_port_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], 'unix://@/path/to/socket/file.sock?db=1')

    def test_socket_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], 'prefix')


class TestDjRedisDatabaseSocketCache(TestDjRedisBothSocketCache):
    def setUp(self):
        super(TestDjRedisDatabaseSocketCache, self).setUp()
        environ['CACHE_URL'] = 'djredisunix:///path/to/socket/file.sock?db=1'

    def test_socket_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], '')


class TestDjRedisPrefixSocketCache(TestDjRedisBothSocketCache):
    def setUp(self):
        super(TestDjRedisPrefixSocketCache, self).setUp()
        environ['CACHE_URL'] = 'djredisunix:///path/to/socket/file.sock?prefix=prefix'

    def test_socket_url_returns_location_and_port_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['LOCATION'], 'unix://@/path/to/socket/file.sock?db=0')

    def test_socket_url_returns_prefix_from_url(self):
        config = django_cache_url.config()
        assert_equals(config['KEY_PREFIX'], 'prefix')


class TestDjHiredisDatabaseSocketCache(TestDjRedisDatabaseSocketCache):
    def setUp(self):
        super(TestDjHiredisDatabaseSocketCache, self).setUp()
        environ['CACHE_URL'] = 'djhiredisunix:///path/to/socket/file.sock?db=1'

    def test_hiredis_url_sets_hiredis_parser(self):
        config = django_cache_url.config()
        assert_equals(config['OPTIONS']['PARSER_CLASS'],
                      'redis.connection.HiredisParser')


class TestDjHiredisPrefixSocketCache(TestDjRedisPrefixSocketCache):
    def setUp(self):
        super(TestDjHiredisPrefixSocketCache, self).setUp()
        environ['CACHE_URL'] = 'djhiredisunix:///path/to/socket/file.sock?prefix=prefix'

    def test_hiredis_url_sets_hiredis_parser(self):
        config = django_cache_url.config()
        assert_equals(config['OPTIONS']['PARSER_CLASS'],
                      'redis.connection.HiredisParser')
