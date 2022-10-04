#!/usr/bin/env python
# coding=utf-8

import os
import re
import shutil
import string
from importlib import import_module
from importlib.util import find_spec
from os.path import dirname
from os.path import join, exists, abspath
from shutil import move

from scrapy.commands import startproject, genspider
from scrapy.commands.genspider import extract_domain, sanitize_module_name
from scrapy.exceptions import UsageError
from scrapy.utils.project import get_project_settings
from scrapy.utils.template import render_templatefile, string_camelcase


class StartProjectBuilder(startproject.Command):
    def __init__(self):
        super().__init__()
        self.settings = get_project_settings()
        self.settings['TEMPLATES_DIR'] = F'{os.path.abspath(r"..")}/scrapy-template-plus/templates'
        self.TEMPLATES_TO_RENDER = (
            ('scrapy.cfg',),
            ('${project_name}', 'settings.py.tmpl'),
            ('${project_name}', 'items.py.tmpl'),
            ('${project_name}', 'pipelines.py.tmpl'),
            ('${project_name}', 'middlewares.py.tmpl'),

            ('${project_name}', 'run.py.tmpl'),
            ('${project_name}', 'components/extensions/report.py.tmpl'),
            ('${project_name}', 'components/middlewares/monitor.py.tmpl'),
            ('${project_name}', 'components/middlewares/retry.py.tmpl'),
            ('${project_name}', 'components/middlewares/aiohttpcrawl.py.tmpl'),
            ('${project_name}', 'components/middlewares/seleniumcrawl.py.tmpl'),
            ('${project_name}', 'components/pipelines/sql.py.tmpl'),
            ('${project_name}', 'components/pipelines/file.py.tmpl'),
        )

    def run(self, args, opts):
        if len(args) not in (1, 2):
            raise UsageError()

        project_name = args[0]
        project_dir = args[0]

        if len(args) == 2:
            project_dir = args[1]

        if exists(join(project_dir, 'scrapy.cfg')):
            self.exitcode = 1
            print(f'【提示】: scrapy.cfg 已经存在于 {abspath(project_dir)}')
            return abspath(project_dir)

        if not self._is_valid_name(project_name):
            self.exitcode = 1
            return

        self._copytree(self.templates_dir, abspath(project_dir))
        move(join(project_dir, 'module'), join(project_dir, project_name))
        for paths in self.TEMPLATES_TO_RENDER:
            path = join(*paths)
            tplfile = join(project_dir, string.Template(path).substitute(project_name=project_name))
            render_templatefile(tplfile, project_name=project_name, ProjectName=string_camelcase(project_name))
        print(F"\n项目【 {project_name} 】已创建！ \n项目路径：{abspath(project_dir)}")
        return abspath(project_dir)

    @staticmethod
    def is_valid_name(project_name):
        def _module_exists(module_name):
            spec = find_spec(module_name)
            return spec is not None and spec.loader is not None

        if not re.search(r'^[_a-zA-Z]\w*$', project_name):
            print('【提示】: 项目名称必须以字母开头且仅包含\n'
                  ' 数字、字母 和 英文下划线')
        elif _module_exists(project_name):
            print(f'【提示】: 项目 {project_name!r} 已经创建好！')
            return True
        else:
            return True
        return False


class GenSpiderBuilder(genspider.Command):
    def __init__(self):
        super().__init__()
        self.settings = get_project_settings()
        self.settings['TEMPLATES_DIR'] = F'{os.path.abspath(r"../..")}/scrapy-template-plus/templates'

    def run(self, args, opts):
        name, url = args[0:2]
        domain = extract_domain(url)
        module = sanitize_module_name(name)

        if self.settings.get('BOT_NAME') == module:
            print("【提示】: 无法创建与您的项目同名的蜘蛛!")
            return

        self._genspider(module, name, domain, 'basic', join(self.templates_dir, f'basic.tmpl'))

    def _genspider(self, module, name, domain, template_name, template_file):
        """Generate the spider module, based on the given template"""
        capitalized_module = ''.join(s.capitalize() for s in module.split('_'))
        tvars = {
            'project_name': self.settings.get('BOT_NAME'),
            'ProjectName': string_camelcase(self.settings.get('BOT_NAME')),
            'module': module,
            'name': name,
            'domain': domain,
            'classname': f'{capitalized_module}Spider'
        }
        if self.settings.get('NEWSPIDER_MODULE'):
            spiders_module = import_module(self.settings['NEWSPIDER_MODULE'])
            spiders_dir = abspath(dirname(spiders_module.__file__))
        else:
            spiders_module = None
            spiders_dir = "."
        spider_file = f"{join(spiders_dir, module)}.py"
        shutil.copyfile(template_file, spider_file)
        render_templatefile(spider_file, **tvars)
        print(f"爬虫样例 [{name!r}] 已创建！",
              end=('' if spiders_module else '\n'))
        if spiders_module:
            print(f"模块:\n  {spiders_module.__name__}.{module}")


class CheckInput:
    @staticmethod
    def check_project_name(project_name):
        if not StartProjectBuilder().is_valid_name(project_name):
            while True:
                re_input = input('项目名称 输入有误！请重新输入：')
                if StartProjectBuilder().is_valid_name(re_input):
                    return re_input
        return project_name


if __name__ == '__main__':
    print('#' * 40)
    print('#  欢迎使用 scrapy-template-plus 生成器  #')
    print('#' * 40)
    _project_name = CheckInput().check_project_name(input('请输入项目名（首位为字母，后面可以是数字字母下划线）：'))

    print(F'您的项目名称为：[{_project_name}]')
    _spider_name = input('请输入爬虫名：')
    print(F'您的爬虫名称为：[{_spider_name}]')
    _spider_host = input('请输入爬行限制域名范围：')
    print(F'您的爬行限制域名范围为：[{_spider_host}]')

    project_dir = StartProjectBuilder().run((F'{_project_name}',), ())
    os.chdir(abspath(project_dir))
    GenSpiderBuilder().run((_spider_name, _spider_host), ())
    print('生成完毕！')
