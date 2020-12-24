# 牛客竞赛 Ghost Generator

由于牛客的某些设置比较神秘，所以得分好几个阶段来处理。

请在使用前清空当前文件夹的 `*.ndjson`。

1. 修改 `nowcoder_common.py` 中开头的几个信息，例如 `cookie`, `contestid`, `start_time`, `end_time`

2. 运行 `step1_fetch.py` 将数据爬取到本地

   运行时会产生大量警告，是因为爬取牛客的提交列表太难了……只能按名字搜，不能用内部编号搜。

   等到运行结束时请将当前文件夹的 ndjson 文件备份一份

3. 打开生成的 `step2_run.py` 检查修复部分

   由于有些队名很多重复（@耗子尾汁），有些队名比较奇怪（@_, @__），有些队伍交的太多（@大大怪必ak），所以要单独仔细拉取

   请将交的太多的人的前面加上注释，队名全是下划线的每个斜杠前面加\（例如`\_\_`）

   然后运行这个文件。

   如果运行过程中出错，依然可以通过刚才的存档来跳过第二步。

   如果队伍交的太多，你可以点进他的个人主页，然后手动分析一下。[例子](https://ac.nowcoder.com/acm/contest/profile/1030001569/practice-coding?&pageSize=50&search=&statusTypeFilter=-1&languageCategoryFilter=-1&orderType=DESC&page=12)

4. 运行 `step3_merge.py > ghosts.dat` 获得最后文件

   注意需要学校名时将 `teams[t]['userName']` 改为 `teams[t]['team']` 即可

5. 结束啦~

