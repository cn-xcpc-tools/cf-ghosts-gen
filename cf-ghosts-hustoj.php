<?php
static $DB_HOST = "localhost";
static $DB_NAME = "hustoj";
static $DB_USER = "debian-sys-maint";
static $DB_PASS = "123456";

require_once('./include/db_info.inc.php');
require_once('./include/setlang.php');
require_once("./include/const.inc.php");
header("Content-Type: text/plain");

// QUERY contest info
$cid = isset($_GET['id']) ? intval($_GET['id']) : 1000;
$sql = "SELECT `title`, `start_time`, `end_time` FROM `contest` WHERE `contest_id` = ?";
$result = pdo_query($sql, $cid);
if (!$result[0]) { die('No contest '.$cid.' found.'); }
echo '@contest "'.$result[0]['title']."\"\n";
$stt = strtotime($result[0]['start_time']);
echo '@contlen '.((strtotime($result[0]['end_time'])-$stt)/60)."\n";


// QUERY contest problems
$sql = "SELECT `cp`.`problem_id`, `cp`.`num`, `p`.`title` FROM `contest_problem` AS `cp` JOIN `problem` AS `p` ON `cp`.`problem_id` = `p`.`problem_id` WHERE `cp`.`contest_id`=? ORDER BY `cp`.`num`";  $result = pdo_query($sql, $cid);

$prob_map = [];
foreach ($result as $val) {
	$pid = $PID[intval($val['num'])];
	$prob_map[intval($val['problem_id'])] = [ $pid, $val['title'] ];
}

echo '@problems '.count($prob_map)."\n";


// QUERY user info
// We have to ignore some user first
$sql = "SELECT `user_id` FROM `privilege`";
$result = pdo_query($sql);
$priv_map = [];

foreach ($result as $val) {
	$priv_map[$val['user_id']] = 1;
}

$sql = "SELECT `user_id`,`nick`,`school` FROM `users`";
$result = pdo_query($sql);

$user_map = []; $user_map2 = []; $user_tot = 0;
foreach ($result as $key => $val) {
	if (isset($priv_map[$val['user_id']])) continue;
	$user_map[$user_tot] = [ 'teamid' => $user_tot, 'teamname' => $val['nick'] ];
	$user_map2[$val['user_id']] = $user_tot;
	$user_tot += 1;
}

echo '@teams '.count($user_map)."\n";


// QUERY submission info, 4AC, 11CE, other RJ
// For people who haven't summitted once we have to mark up as CE
$sql = "SELECT `problem_id`, `in_date`, `user_id`, `result`, `contest_id` FROM `solution` WHERE `contest_id`=?";
$result = pdo_query($sql, $cid);

$verdict = [ 'RJ', 'RJ', 'RJ', 'RJ', 'OK', 'PE', 'WA', 'TL', 'ML', 'IL', 'RT', 'CE', 'RJ', 'RJ' ];
$sub_map = []; $lastc = [];

foreach ($result as $val) {
	if (isset($user_map2[$val['user_id']])) {
		$n_uid = $user_map2[$val['user_id']];
		$n_pid = $prob_map[intval($val['problem_id'])][0];
		if (!isset($lastc[$n_uid][$n_pid]))
			$lastc[$n_uid][$n_pid] = 0;
		$lastc[$n_uid][$n_pid] += 1;
		$sub_map[] = [
			't' => $n_uid,
			'p' => $n_pid,
			'c' => $lastc[$n_uid][$n_pid],
			's' => strtotime($val['in_date'])-$stt,
			'r' => $verdict[intval($val['result'])]
		];
	}
}

foreach ($user_map as $u) {
	if (!isset($lastc[$u['teamid']])) {
		$sub_map[] = [
			't' => $u['teamid'],
			'p' => 'A',
			'c' => 1,
			's' => 99999,
			'r' => 'CE'
		];
	}
}

echo '@submissions '.count($sub_map)."\n";


// OFFICIAL output details
foreach ($prob_map as $p) {
	echo '@p '.$p[0].','.$p[1].",20,0\n";
}
foreach ($user_map as $t) {
	echo '@t '.$t['teamid'].',0,1,'.str_replace(',', '，', $t['teamname'])."\n";
}
foreach ($sub_map as $s) {
	echo '@s '.$s['t'].','.$s['p'].','.$s['c'].','.$s['s'].','.$s['r']."\n";
}








function pdo_query($sql) {
	$num_args = func_num_args();
	$args = func_get_args();
	$args = array_slice($args, 1, --$num_args);
	try {
		global $DB_HOST, $DB_NAME, $DB_USER, $DB_PASS, $dbh, $OJ_TEMPLATE;
		if (!$dbh) {
			$dbh = new PDO("mysql:host=".$DB_HOST.';dbname='.$DB_NAME, $DB_USER, $DB_PASS,array(PDO::MYSQL_ATTR_INIT_COMMAND => "set names utf8"));
		}
		$sth = $dbh->prepare($sql);
		$sth->execute($args);
		$result = $sth->fetchAll();
		$sth->closeCursor();
		return $result;
	} catch(PDOException $e) {
		if (stristr($e->getMessage(), "Access denied"))
			die("Database account/password fail, check db_info.inc.php");
		else
			die("SQL error,check your sql !");
	}
}