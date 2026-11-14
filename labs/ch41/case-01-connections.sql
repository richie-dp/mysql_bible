-- 第 41 章案例一：连接池漏了，却去扩容。三个终端，全在 mysql-master（3306）。
-- ============ 会话 A：把上限压到 80，制造"贴顶" ============
SET GLOBAL max_connections = 80;
SELECT @@max_connections;
-- ============ 会话 B：开 70 个 Sleep 连接，宿主机执行 ============
-- for i in $(seq 70); do
--   MYSQL_PWD=labpass mysql -h127.0.0.1 -P3306 -uroot -e "SELECT SLEEP(900);" >/dev/null 2>&1 &
-- done
-- 这些连接挂 15 分钟；不要用交互式客户端手工开，太慢
-- ============ 会话 C：诊断，对应附录 D29 / D30 / D31 ============
SELECT USER, SUBSTRING_INDEX(HOST, ':', 1) AS host_ip,
       COMMAND, COUNT(*) AS conns, MAX(TIME) AS max_idle_s
FROM information_schema.processlist
GROUP BY USER, host_ip, COMMAND
ORDER BY conns DESC;
-- 预期：Sleep 一行 70 个，max_idle_s 持续增长；Query 只有你自己的诊断语句
SHOW GLOBAL STATUS WHERE Variable_name IN
  ('Threads_connected', 'Threads_running', 'Max_used_connections',
   'Aborted_clients', 'Connection_errors_max_connections');
-- 预期：Threads_connected ≈ 70+，Threads_running 个位数，Aborted_clients 几乎不动
-- running 低 + connected 高 + aborted 低 = 连接活着没人用，是池子漏了，不是量涨了
-- ============ 会话 C：生成 KILL 清单，先看再执行 ============
SELECT CONCAT('KILL ', ID, ';') AS stmt
FROM information_schema.processlist
WHERE COMMAND = 'Sleep' AND TIME > 60 AND USER = 'root'
ORDER BY TIME DESC LIMIT 20;
-- 确认清单里没有业务连接再执行；随后恢复上限：SET GLOBAL max_connections = 500;
