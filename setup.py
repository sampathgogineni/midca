# !/usr/bin/env python

from setuptools import setup

setup(name='midca',
      version='1.4',
      description='Metacognitive Integrated Dual-Cycle Architecture',
      author='Michael T. Cox and midca Lab',
      author_email='wsri-midca-help@wright.edu',
      packages=['midca',
                'midca.domains',
                'midca.domains.blocksworld',
                'midca.domains.logistics',
                'midca.domains.blocksworld.plan',
                'midca.domains.nbeacons',
                'midca.domains.nbeacons.plan',
                'midca.domains.jshop_domains',
                'midca.domains.jshop_domains.blocks_world',
                'midca.domains.jshop_domains.logistics',
		        'midca.domains.construction_domain',
		        'midca.domains.construction_domain.plan',
		        'midca.domains.restaurant_domain',
		        'midca.domains.restaurant_domain.plan',
                'midca.worldsim',
                'midca.examples',
                'midca.examples._gazebo_baxter',
                'midca.modules',
                'midca.modules._adist',
                'midca.modules._plan',
                'midca.modules._plan.asynch',
                'midca.modules._plan.jShop',
                'midca.modules._goalgen',
                'midca.modules._robot_world',
                'midca.modules._xp_goal',
                'midca.modules.gens',
                'midca.vision',
                'midca.experimental',
                'midca.experimental.baxter',
                'midca.experiment',
                'midca.metamodules'],

      package_data={'': ['*.jar', 'midca.modules._plan.jShop'],
                    '': ['*.txt', 'midca.domains.logistics'],
                    '': ['*.*', 'midca.modules._plan.jShop'],
                    '': ['*.shp', 'midca.domains.jshop_domains.blocks_world']},
      )
