<?php
header("Content-Type: text/plain");

// QUERY contest info
$cid = isset($_GET['id']) ? intval($_GET['id']) : 1;
$sql = "SELECT `name`, `starttime`, `endtime` FROM `contest` WHERE `cid` = ?";
$result = pdo_query($sql, $cid);
if (!$result[0]) { die('No contest '.$cid.' found.'); }
echo '@contest "'.$result[0]['name']."\"\n";
$stt = $result[0]['starttime'];
$ett = $result[0]['endtime'];
echo '@contlen '.(($result[0]['endtime']-$stt)/60)."\n";


// QUERY contest problems
$sql = "SELECT `cp`.`probid`, `cp`.`shortname`, `p`.`name` FROM `contestproblem` AS `cp` JOIN `problem` AS `p` ON `cp`.`probid` = `p`.`probid` WHERE `cp`.`cid` = ? ORDER BY `cp`.`shortname`";  $result = pdo_query($sql, $cid);

$prob_map = [];
foreach ($result as $val) {
	$pid = intval($val['probid']);
	$prob_map[$pid] = [ $val['shortname'] , $val['name'] ];
}

echo '@problems '.count($prob_map)."\n";


// QUERY team info
$sql = "SELECT `t`.`teamid`, `t`.`name`, `a`.`name` AS `school` FROM `team` AS `t` JOIN `team_category` AS `c` ON `t`.`categoryid` = `c`.`categoryid` JOIN `team_affiliation` AS `a` ON `t`.`affilid` = `a`.`affilid` WHERE `c`.`sortorder` = 0";  $result = pdo_query($sql);

$user_map = []; $user_map2 = []; $user_tot = 0;
foreach ($result as $key => $val) {
	if (isset($priv_map[$val['teamid']])) continue;
	$user_map[$user_tot] = [ 'teamid' => $user_tot, 'teamname' => str_replace(',', '，', $val['name']) . ' (' . $val['school'] . ')' ];
	$user_map2[$val['teamid']] = $user_tot;
	$user_tot += 1;
}

echo '@teams '.count($user_map)."\n";


// QUERY submission info, 4AC, 11CE, other RJ
// For people who haven't summitted once we have to mark up as CE
$sql = "SELECT `s`.`probid`, `s`.`submittime`, `s`.`teamid`, `j`.`result` FROM `submission` AS `s` JOIN `judging` AS `j` ON `s`.`submitid` = `j`.`submitid` WHERE `s`.`cid` = ? AND `j`.`valid` = 1 ORDER BY `s`.`submittime`";  $result = pdo_query($sql, $cid);

$verdict = [
	'correct' => 'OK',
	'wrong-answer' => 'WA',
	'run-error' => 'RT',
	'timelimit' => 'TL',
	'memory-limit' => 'ML',
	'no-output' => 'WA',
	'output-limit' => 'IL',
	'compiler-error' => 'CE'
];

$sub_map = []; $lastc = [];

foreach ($result as $val) {
	if (isset($user_map2[$val['teamid']])) {
		if ($val['submittime'] > $ett) continue;
		$n_uid = $user_map2[$val['teamid']];
		$n_pid = $prob_map[intval($val['probid'])][0];
		if (!isset($lastc[$n_uid][$n_pid]))
			$lastc[$n_uid][$n_pid] = 0;
		$lastc[$n_uid][$n_pid] += 1;
		$sub_map[] = [
			't' => $n_uid,
			'p' => $n_pid,
			'c' => $lastc[$n_uid][$n_pid],
			's' => intval($val['submittime']-$stt),
			'r' => $verdict[$val['result']]
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
		global $dbh;
		if (!$dbh) {
			$dbh = new PDO("mysql:host=localhost;dbname=domjudge", "root"/*, "password"*/);
			$dbh->query('SET NAMES utf8mb4');
		}
		$sth = $dbh->prepare($sql);
		$sth->execute($args);
		$result = $sth->fetchAll();
		$sth->closeCursor();
		return $result;
	} catch(PDOException $e) {
		if (stristr($e->getMessage(), "Access denied"))
			die("Database account/password fail, check db_info.inc.php\n");
		else
			die("SQL error,check your sql !\n");
	}
}
