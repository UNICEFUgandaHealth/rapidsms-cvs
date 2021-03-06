from setuptools import setup, find_packages

setup(
    name='rapidsms-cvs',
    version='0.1',
    license="BSD",

    install_requires=[
        "rapidsms",
        'rapidsms-xforms',
        'rapidsms-auth',
        'rapidsms-polls',
        'rapidsms-httprouter',
        'django-extensions',
        'django-uni-form',
        'django-eav',
        'health-models',
        'rapidsms-contact',
        'rapidsms-generic',
        'uganda-common',
    ],

    dependency_links=[
        "http://github.com/daveycrockett/healthmodels/tarball/master#egg=health-models",
        "http://github.com/daveycrockett/rapidsms-xforms/tarball/master#egg=rapidsms-xforms",
        "http://github.com/daveycrockett/auth/tarball/master#egg=rapidsms-auth",
        "http://github.com/daveycrockett/rapidsms-polls/tarball/master#egg=rapidsms-polls",
        "http://github.com/daveycrockett/rapidsms-httprouter/tarball/master#egg=rapidsms-httprouter",
        "http://github.com/mvpdev/django-eav/tarball/master#egg=django-eav",
        "http://github.com/mossplix/rapidsms-contact/tarball/master#egg=rapidsms-contact",
        "http://github.com/daveycrockett/rapidsms-generic/tarball/master#egg=rapidsms-generic",
        "http://github.com/mossplix/uganda_common/tarball/master#egg=uganda-common",
    ],

    description='The community vulnerability surveillance program deployed in Uganda for the VHT program',
    long_description=open('README.rst').read(),
    author='David McCann',
    author_email='david.a.mccann@gmail.com',

    url='http://github.com/daveycrockett/rapidsms-cvs',
    #download_url='http://github.com/daveycrockett/rapidsms-cvs/downloads',

    include_package_data=True,

    packages=find_packages(),
    package_data={'cvs':['templates/*/*.html', 'templates/*/*/*.html', 'static/*/*']},
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
