# scrapy-template-plus
Scrapy模板生成器，该项目集成了常用中间件，避免重复造轮子

---

在 [Scrapy (2.6.2 版本)](https://docs.scrapy.org/en/2.6/) 模板的基础上，集成了一些常用的功能模块。



## 项目结构

```bash
├─scrapy-template-plus
│  │  README.md     ## 说明文件
│  │  
│  └─templates     ## 模板目录
│      ├─project     ## 创建项目的模板目录
│      │  │  scrapy.cfg
│      │  │  
│      │  └─module
│      │      │  items.py.tmpl     ## item、itemloader，定义项目字段及字段数据清洗
│      │      │  middlewares.py.tmpl     ## middlerwares，原始无改动，可自定义下载中间件
│      │      │  pipelines.py.tmpl     ## pipeline，原始无改动，可自定义数据传输通道
│      │      │  run.py.tmpl     ## 批量运行爬虫入口
│      │      │  settings.py.tmpl     ## 项目全局设置
│      │      │  __init__.py
│      │      │  
│      │      ├─components     ## 组件目录
│      │      │  │  __init__.py
│      │      │  │  
│      │      │  ├─extensions     ## 扩展目录
│      │      │  │      report.py.tmpl     ## 爬虫运行完毕的报告组件
│      │      │  │      __init__.py
│      │      │  │      
│      │      │  ├─middlewares     ## 中间件目录
│      │      │  │  │  aiohttpcrawl.py.tmpl     ## AioHttp下载器
│      │      │  │  │  blacklist.py     ## 强制延迟黑名单、禁止访问黑名单
│      │      │  │  │  monitor.py.tmpl     ## 监控中间件
│      │      │  │  │  proxy.py     ## 代理中间件
│      │      │  │  │  randomua.py     ## 随机UA中间件
│      │      │  │  │  retry.py.tmpl     ## 重试中间件
│      │      │  │  │  seleniumcrawl.py.tmpl     ## Selenium下载器（基于undetected-chromedriver）
│      │      │  │  │  __init__.py
│      │      │  │  │  
│      │      │  │  └─browser_plugins     ## Selenium下载器需要加载的反指纹插件
│      │      │  │      ├─audioContext_fingerprint_defender_0.1.6_0
│      │      │  │      ├─canvas_fingerprint_defender_0.1.9_0
│      │      │  │      ├─font_fingerprint_defender_0.1.3_0
│      │      │  │      ├─webgl_fingerprint_defender_0.1.5_0
│      │      │  │      └─webrtc-control_0.3.0_0
│      │      │  │                  
│      │      │  ├─pipelines
│      │      │  │      file.py     ## 文件的pipeline（文件存储）
│      │      │  │      nosql.py     ## NoSQL的pipeline（包含：异步MongoDB）
│      │      │  │      sql.py.tmpl     ## SQL的pipeline（包含：异步MySQL）
│      │      │  │      __init__.py
│      │      │  │      
│      │      │  └─utils     ## 工具类目录
│      │      │          dingding.py     ## 钉钉消息推送工具类
│      │      │          orc.py     ## ORC图片识别工具类
│      │      │          parser.py     ## TextResponse的封装，增加 JSONPath支持
│      │      │          secure.py     ## 加密算法工具类
│      │      │          __init__.py     ## 基础工具类（Selenium下载器截图存储、列表翻页转换工具类、等）
│      │      │          
│      │      └─spiders
│      │              __init__.py
│      │              
│      └─spiders     ## 创建爬虫的模板目录
│              basic.tmpl     ## 基于books.toscrape.com的爬虫样例
│              
└─scrapy-template-plus-builder
       requirements.txt     ## 项目环境
       builder-run.py     ## 根据 scrapy-template-plus 创建项目、爬虫的入口程序

```



## 开始使用

下载项目到某个目录，然后运行 `builder-run.py`，按提示操作即可

```bash
# 下载到某个目录中
/某个目录/
    ├─scrapy-template-plus
    │  │  README.md     ## 说明文件
    │  └─templates
    │      └─project ## 省略里面的文件
    │
    └─scrapy-template-plus-builder
           requirements.txt      ## ⒈先安装环境（推荐conda创建 python3.8的环境），命令：pip install -r requirements.txt
           builder-run.py      ## ⒉再运行它，⒊最后用IDE加载生成的项目，将项目标记为 “源 根”（source root）
```



## 使用说明

### spiders

> 以 [http://books.toscrape.com/](http://books.toscrape.com/) 网址为例，提供了一套爬虫模板，正常情况，builder生成好文件就可以直接运行，测试环境是否安装正确

* `name` ：为爬虫名称，需确保唯一

* `allowed_domains`：爬行限制，默认禁用，实际使用需要按情况设置

* `start_urls`：爬虫的种子，提供一种翻页参数，可以生成要爬行的列表页集合

  翻页参数，说明：

    * 常用表达式：`【起始数字-爬行的页数】`，例如`http://books.toscrape.com/catalogue/page-【1-2】.html`，等价于`http://books.toscrape.com/catalogue/page-1.html`、`http://books.toscrape.com/catalogue/page-2.html`
    * 等差表达式：`【起始数字-爬行的页数:公差】`，例如`【0-5:2】`等价于`0、2、4、6、8`
    * 等比表达式：`【起始数字-爬行的页数::公比】`，没啥用

* `start_requests`、`parse`：正常写爬虫逻辑即可，推荐把字段提取逻辑都放在 `item` 中处理

* `__name__`：main方法，测试调试用、小批量采集直接运行

* 数据传递：约定用`kwargs`传递业务逻辑数据，与中间件交互用`meta`



### run.py

在`tasks_list`数组中添加爬虫的`name`，调度器填写运行的定时器，可以批量运行爬虫



### items.py

* `item` 中定义爬虫的数据字段

* `itemloader`中填充字段数据，传递过来的`response`为`ResponseParser`，其中增加了`JSONPath`表达式的支持



### settings.py

* `DEBUG_FILE_NAME`：存储调试文件的文件名规则

* 【日志】设置：生产环境可开启

* 【调试】：将采集的数据临时存到当前爬虫目录的`debug/data`文件夹下

* 监控报告

    * 【监控】设置：支持钉钉消息推送，注释掉或设置空可关闭该功能
    * 【报告】设置：不设置的话，默认为“监控设置”设置的钉钉信息

* 存储设置

    * 【存储】设置：支持`MySQL`、`MongoDB`数据库存储，多张表需要修改`multi_table_name`处逻辑

* 采集策略

    * 【代理IP】设置：开启功能需要设置`IP_PROXY_SERVICE`为`True`

    * 【请求最大并发数】设置：需要根据目标网站的具体情况进行设置

    * 【下载延迟】设置：需要根据目标网站的具体情况进行设置，需要`JA3伪装`要设置小于`0.5`

    * 【下载超时】设置：需要根据目标网站的具体情况进行设置

    * 【下载重试】设置：
        * `RETRY_LOG_404`会记录所有状态码为`404`的网址，调试查错用
        * `RETRY_LOG_BAN`会记录被禁访问的网址，在`blacklist.py`文件的`ban_list`中添加

    * 【自动调频功能开关、延迟初始值、调整幅度】设置：

      > 摸清网址抓取频率后可关闭、需要`JA3伪装`需加代理再关闭

    * 【通用爬虫策略】：通用爬虫的调度与定向不同，可以在这里设置，默认关闭

* 伪装策略

    * 【User-Agent】设置：可以固定UA
    * 【随机User-Agent】设置，查看支持平台：[https://github.com/ihandmine/anti-useragent/blob/main/doc/README_ZH.md#支持平台](https://github.com/ihandmine/anti-useragent/blob/main/doc/README_ZH.md#支持平台)
        * `RANDOM_USER_AGENT`为`True`时启用
        * `RANDOM_USER_AGENT_PLATFORM`数组中添加平台参数，如`['windows', 'linux', 'mac']`
        * `RANDOM_USER_AGENT_BROWSER`数组中添加浏览器参数，如`['chrome', 'firefox']`
    * 【通用请求头】设置：添加通用Header

* 中间件

    * `SPIDER_MIDDLEWARES`：

        * 爬虫异常监控：`components.middlewares.monitor.ExceptionSpiderMiddleware`

    * `DOWNLOADER_MIDDLEWARES`

        * 中间件异常监控：`components.middlewares.monitor.ExceptionMiddleware`

        * 随机UA：`components.middlewares.randomua.RandomUADownloadMiddleware`

        * 重试日志记录：`components.middlewares.retry.RetryLogMiddleware`

          > 记录重试失败超过上限的网址、404的网址及黑名单中的网址，并分别记录到不同文件中

        * 代理IP：`components.middlewares.proxy.ProxyMiddleware`

        * AiohttpRequest：`components.middlewares.aiohttpcrawl.AiohttpCrawlMiddleware`

          > 异步请求，速度快，使用时候需要考虑风控

        * SeleniumRequest：`components.middlewares.seleniumcrawl.SeleniumCrawlMiddleware`

          > 默认关闭，需要用到的时候在启用它
          >
          > 无须下载WebDriver，内置`ChromeDriverManager`，缓存有效期100天，可自行修改

    * `ITEM_PIPELINES`

        * MYSQL：`components.pipelines.sql.SqlPipeline`
        * MongoDB：`components.pipelines.nosql.MongoDBPipeline`
        * File：`components.pipelines.file.FilePipeline`
        * Scrapy-Redis：`scrapy_redis.pipelines.RedisPipeline`

    * `EXTENSIONS`

        * scrapy.extensions.telnet.TelnetConsole：禁用，有需要可以打开

        * 推送报告：`components.extensions.report.Reporter`

          > 采集完成会把采集结果发送到钉钉中

    * `Download Handlers`

      > 可以开启 scrapy 的 `H2DownloadHandler`

    * JA3伪装

      > ```python
      > DOWNLOADER_CLIENTCONTEXTFACTORY = 'anti_useragent.utils.scrapy_contextfactory.Ja3ScrapyClientContextFactory'
    
* Asyncio 支持

  > **必须开启**

* 【HTTP缓存】：根据业务情况选择性的设置，多用于本地重跑字段

* 允许全部HTTP状态码

  > 若返回自定义状态码 `-1` ，则代表该请求已达到重试上限，可自行判定取舍
  >
  > ```python
  > HTTPERROR_ALLOW_ALL = True
  > ```

* Scrapy-Redis 支持

  > 默认注释掉了。单机爬虫测试无误后可根据情况开启



## 爬虫样例

详见另一个项目 👉 [scrapy_tplp_demos](scrapy_tplp_demos)

