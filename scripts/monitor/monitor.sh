#!/bin/bash
dirpath="$(cd "$(dirname "$0")" && pwd)"
cd $dirpath
g_debug="false"
rpc_ip=
rpc_port=
node_list=
node_count=0
node_idx=0
mem_thres=20
cpu_thres=600
group_list_str="1"
expected_cons=1
program="fisco-bcos"
alert_receiver="asherli"
alert_title="fisco-bcos-2.0-monitor:"$(date)
restart="false"
export receiver_addr=https://sc.ftqq.com/SCU44538T27d765b798c1456ab1ecb42a2c986e665c63946211db0.send

function LOG_ERROR()
{
    content=${1}
    time=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "\033[31m"[${time}] ${content}"\033[0m\n"
}

function LOG_INFO()
{
    content=${1}
    time=$(date "+%Y-%m-%d %H:%M:%S")
    echo -e "\033[32m"[${time}] ${content}"\033[0m"
}

function execute_cmd()
{
    command="${1}"
    #LOG_INFO "RUN: ${command}"
    eval ${command}
    ret=$?
    if [ $ret -ne 0 ];then
        LOG_ERROR "FAILED execution of command: ${command}"
        exit 1
    fi
}

function debug()
{
        g_debug="true"
}


alarm() {
   # do serverchan
   echo "${alert_title}: $1"
   alert_ip=$(/sbin/ifconfig eth0 | grep inet | awk '{print $2}')
   time=$(date "+%Y-%m-%d %H:%M:%S")
   system_id=123
   curl --data "text=${alert_title}" --data "desp={alertList:[{'alert_title':'$alert_ip','sub_system_id':'$system_id','alert_info':'$time:$1','alert_ip':'$alert_ip','alert_reciver':'$alert_receiver'}]}" $receiver_addr
   echo -e "\n"
}

# restart node
restart() {
        stopfile=${1/start/stop}
        startfile="${1}"
        execute_cmd "bash $stopfile"
        sleep 3
        execute_cmd "bash $startfile"
}

# execute RPC command
function execRpcCommand() 
{
    local all_group="${1}"
    local functionName="${2}"
    local group_id="${3}"
    if [ "${all_groups}" == true ];then
        rpc_command="curl --fail --silent --show-error -X POST --data '{\"jsonrpc\":\"2.0\",\"method\":\"${functionName}\",\"params\":[],\"id\":83}' http://${rpc_ip}:${rpc_port}"
    else
        rpc_command="curl --fail --silent --show-error -X POST --data '{\"jsonrpc\":\"2.0\",\"method\":\"${functionName}\",\"params\":[${group_id}],\"id\":83}' http://${rpc_ip}:${rpc_port}"
    fi
    execute_cmd "${rpc_command}"
}

# parse INI
function read_ini
{
INIFILE=$1
SECTION=$2
ITEM=$3
ini_value="`awk -F '=' '/\['$SECTION'\]/{a=1}a==1&&$1~/'$ITEM'/{print $2; exit}' $INIFILE`"
echo ${ini_value}
}

function get_json_value()
{
  local json=$1
  local key=$2
  if [[ -z "$3" ]]; then
    local num=1
  else
    local num=$3
  fi
  local value=$(echo "${json}" | awk -F"[:,}]" '{for(i=1;i<=NF;i++){if($i~/'${key}'\042/){print $(i+1)}}}' | tr -d '"' | sed -n ${num}p)
  echo "${value}"
}

# get total consensus count of this chain
function get_total_consensus_node_count()
{
    local group_id="${1}"
    # obtain node_list
    node_list_json=$(execRpcCommand "false" "getSealerList" ${group_id})
    node_list_str=$(get_json_value ${node_list_json} "result" |  cut -d'[' -f2 | cut -d']' -f1)
    IFS_old=$IFS
    IFS=',';
    node_list=(${node_list_str})
    node_count=${#node_list[@]}
    IFS=${IFS_old}

    echo "$node_count"
}

# check cpu and memory
function check_resource()
{
    local node_name=$(basename "${1}")
    local node_dir="${node_name}/fisco-bcos"
    local cpu_usage=$(ps aux | grep ${program} | grep -v grep | grep ${node_dir} | awk '{print $3}')
    local mem_usage=$(ps aux | grep ${program} | grep -v grep | grep ${node_dir} | awk '{print $4}')
    ret=0
    if [ `echo "$mem_usage>$mem_thres" | bc` -eq "1" ];then
        error_msg="[node: ${node_name}, mem_thres: ${mem_thres}, cur_mem: ${mem_usage}, cur_cpu: [${cpu_usage}]] in use of over-threshold memory"
        LOG_ERROR "${error_msg}"
        alarm "${error_msg}"
        ret=1
    fi
    if [ `echo "$cpu_usage>$cpu_thres" | bc` -eq "1" ];then
        error_msg="[node: ${node_name}, cpu_thres: ${cpu_thres}, cur_cpu: [${cpu_usage}, cur_mem: ${mem_usage}]] in use of over-threshold cpu"
        LOG_ERROR "${error_msg}"
        alarm "${error_msg}"
        ret=1
    fi
    return $ret;
}

function check_process()
{
    local node_name=$(basename "${1}")
    local node_dir="${node_name}/fisco-bcos"
    # check if process id exist
    fisco_pwd=$(ps aux | grep  "$node_dir" |grep "${program}"|grep -v "grep")
    [ -z "$fisco_pwd" ] &&  {
                [ "$restart" == "true" ] && {
                        alarm "ERROR! [node:${node_dir}] process has been shut-down, restart now!"
                        LOG_ERROR "ERROR! [node: ${node_dir}] process has been shut-down, restart now!"
                        restart $startfile
                        return 1
                }
                alarm "ERROR! [node:${node_dir}] process has been shut-down, you should restart it!"
                LOG_ERROR "ERROR! [node:${node_dir}] process has been shut-down, you should restart it!"
                return 1
     }
     return 0
}

function obtain_rpc_ip()
{
    local config_ip="${1}"
    rpc_ip="${config_ip}"
    if [ "${config_ip}" == "0.0.0.0" ];then
        rpc_ip=$(/sbin/ifconfig | grep inet | grep -v "127.0.0.1" | sort | head -n 1 | awk '{print $2}')
    fi
    echo "${rpc_ip}"
}

function restartNode()
{
    local prefix="${1}"
    local retJson="${2}"
    local startfile="${3}"
    if [[ -z "${retJson}" ]];then
        error_str="${prefix} for cannot connect to $rpc_ip:$rpc_port"
        if [ "$restart" == "true" ];then
            error_str="Trying to restart node: ${error_str}"
            restart ${startfile}
        fi
        alarm "${error_str}"
        LOG_ERROR "${error_str}"
        return 1
    fi
}

function isSealer()
{
    local group_id="${1}"
    local startfile="${2}"
    local node_dir="${3}"
    consensusStatusJson=$(execRpcCommand "false" "getConsensusStatus" ${group_id})
    # get nodeIdx
    node_index=$(get_json_value "${consensusStatusJson}" "index" 1)

    local error_prefix="getConsensusStatus ERROR: [node: ${node_dir}][group:${group_id}] is not working properly "
    restartNode ${error_prefix} "${node_index}" "${startfile}"
    # callback jsonRPC interface failed
    if [ $? -eq 1 ];then
        return 1
    fi
    # get view
    view=$(get_json_value "${consensusStatusJson}" "currentView" 1)
    echo "${node_index}" "${view}"
}

function check_connections()
{
    local group_id="${1}"
    local startfile="${2}"
    local node_dir="${3}"
    peersJson=$(execRpcCommand "false" "getPeers" ${group_id})
    
    error_str_prefix="getPeers ERROR: [node: ${node_dir}][group:${group_id} is not working properly "
	
    restartNode "${error_str_prefix}" "${peersJson}" "${startfile}"
    # callback jsonRPC interface failed
    if [ $? -eq 1 ];then
        return 1
    fi
    peers=$(echo "${peersJson}" | jq -r '.result[].NodeID')
    
    if [ -z "${peers}" ];then
        i=0
    else
        i=$(echo "${peers}" | wc -l)
    fi
    if [ $i -lt ${expected_cons} ];then
	error_str="${error_str_prefix} for network connection failures, expected=${expected_cons}, real connections is ${i}"
        if [ "$restart" == "true" ];then
                error_str="Trying to restart node for: ${error_str}"
                restart $startfile
        fi
        alarm "${error_str}"
        LOG_ERROR "${error_str}"
        return 1
    fi
}


function check_observer()
{
    local group_id="${1}"
    local startfile="${2}"
    local node_dir="${3}"
    syncStatusJson=$(execRpcCommand "false" "getSyncStatus" ${group_id})
    error_str_prefix="check status of observer node ERROR: [node: ${node_dir}][group:${group_id}] is not working properly "
    
    blockNumberJson=$(get_json_value "${syncStatusJson}" "blockNumber" 1)
    restartNode "${error_str_prefix}" "${blockNumberJson}" "${startfile}"
    # callback jsonRPC interface failed
    if [ $? -eq 1 ];then
        return 1
    fi
 

    peerBlockNumbers=$(echo "${syncStatusJson}" | jq -r '.result.peers[].blockNumber')
    # get blockNumber for all nodes
    currentBlockNumber=$((blockNumberJson))
    for blockNumberStr in ${peerBlockNumbers}
    do
        blockNumber=$((blockNumberStr))
        minBlockNumber=$blockNumber
        if [ ${blockNumber} -ge 1 ];then
            minBlockNumber=$[${blockNumber} - 1]
        fi
        if [[ ${currentBlockNumber} -lt ${minBlockNumber} ]];then
            error_str="${error_str_prefix} for not syncing block from other nodes: height ${blockNumber}, height of other node: ${blockNumberJson}"
            if [ "$restart" == "true" ];then
                error_str="Trying to restart node: ${error_str}"
                restart $startfile
            fi
            alarm "${error_str}"
            LOG_ERROR "${error_str}"
            return 1
        fi
    done
}


function check_pbft_view()
{
    local group_id="${1}"
    local startfile="${2}"
    local node_dir="${3}"
    local pbft_view="${4}"
    local node=$(basename ${node_dir})
    # get blocknumber
    height_json=$(execRpcCommand "false" "getBlockNumber" ${group_id})
    height=$(get_json_value ${height_json} "result" | cut -d'[' -f2 | cut -d']' -f1)
    LOG_INFO "[node: ${node_dir}] [group: ${group_id}] current block number:${height}"
    [[ -z "$height" ]] && {
        [ "$restart" == "true" ]  && {
                alarm "ERROR![node: ${node_dir}] [group: ${group_id}] Cannot connect to $rpc_ip:$rpc_port $height"
                restart $startfile
                return 1
        }
        LOG_ERROR "ERROR! [node: ${node_dir}] [group: ${group_id}] Cannot connect to $rpc_ip:$rpc_port $height"
        return 1
    }
     # get prev height
     local height_file="$nodedir/${node}.${group_id}.height"
     local prev_height=0
     [ -f $height_file ] && prev_height=$(cat $height_file)
     local heightvalue=$(printf "%d\n" "$height")
     local prev_heightvalue=$(printf "%d\n" "$prev_height")
     # get prev view
     local view_file="$nodedir/${node}.${group_id}.view"
     local prev_view=0
     [ -f $view_file ] && prev_view=$(cat $view_file)
     local viewvalue=$(printf "%d\n" "$pbft_view")
     local prev_viewvalue=$(printf "%d\n" "$prev_view")
     # check if blocknumber of pbft view already change, if all of them is the same with before, the node may not work well.
     [  $heightvalue -eq  $prev_heightvalue ] && [ $viewvalue -eq  $prev_viewvalue ] && {
             [ "$restart" == "true" ] && {
                        alarm "ERROR! [node: ${node_dir}][group: ${group_id}] $rpc_ip:$rpc_port is not working properly: height $height and view $view no change"
                        return 1
                }
                LOG_ERROR "ERROR! [node: ${node_dir}][group: ${group_id}] $rpc_ip:$rpc_port is not working properly: height $height and view $view no change"
                return 1
      }
      echo $height > $height_file
      echo $view > $view_file
}

function check_group_work_properly()
{
    local node_dir="${1}"
    local group_id="${2}"
    local start_file=${1}/start.sh
    # check connection
    check_connections "${group_id}" "${start_file}" "${node_dir}"
    if [ $? -eq 1 ];then
       return 1
    fi
            
    local node_info=$(isSealer ${group_id} ${start_file} ${node_dir})
    if [ "${node_info}" == "1" ];then
        return 1
    fi
    # get node index
    local node_index=$(echo ${node_info} | cut -d ' ' -f1)
    local currentView=$(echo ${node_info} | cut -d ' ' -f2)
    if [ "${node_index}" == "65535" ];then
	    LOG_INFO "===== Observer node, check blockNumber only=== "
        check_observer "${group_id}" "${start_file}" "${node_dir}"
        if [ $? -eq 1 ];then
		return 1
        fi
    else
        # check pbft view
        check_pbft_view "${group_id}" "${start_file}" "${node_dir}" "${currentView}"
        if [ $? -eq 1 ];then
		return 1
        fi
    fi
    return 0
}

function get_group_list()
{
    group_list_json=$(execRpcCommand "true" "getGroupList" )
    group_list_str=$(get_json_value ${group_list_json} "result" | cut -d'[' -f2 | cut -d']' -f1)
    IFS_old=${IFS}
    IFS=','
    group_list=(${group_list_str})
    IFS=${IFS_old}
}

function check_all_group_work_properly()
{
    local node_dir="${1}"
    # get groups from rpc
    get_group_list
    for group in ${group_list[*]};do
        check_group_work_properly "${node_dir}" "${group}" 
    done
}

# check if node$1 is work well
function check_node_work_properly()
{
    # node dir
    nodedir=$1
    # should restart the node when it not work properly
    # start shell
    startfile=$1/start.sh
    # stop shell
    stopfile=$1/stop.sh
    # config.ini for this node
    configini=$1/config.ini
    
    config_ip=$(read_ini ${configini} rpc jsonrpc_listen_ip)
    #obtain rpc ip according to config_ip
    LOG_INFO "=== config_ip:"${config_ip}
    rpc_ip=$(obtain_rpc_ip "${config_ip}")
    LOG_INFO "=== rpc_ip:"${rpc_ip}
    rpc_port=$(read_ini ${configini} rpc jsonrpc_listen_port)
    LOG_INFO "=== rpc_port:"${rpc_port}
    # check process
    check_process "${nodedir}"
    if [[ $? == 1 ]];then
        return 1
    fi
    
    check_resource "${nodedir}"

    if [[ $? == 1 ]];then
        return 1
    fi
    # check all groups work properly
    check_all_group_work_properly "${nodedir}"
    return 0
}

# check all node of this server, if all node work well.
function check_all_node_work_properly()
{
        for configfile in `ls $dirpath/node*/config.ini`
        do
            nodedir=$(dirname $configfile)
            echo "*******************check ${nodedir} START**********************"
            check_node_work_properly $nodedir
            time_point=$(($(date +%s) - 60))
            do_log_analyze_by_time_point $nodedir $time_point
            echo "*******************check ${nodedir} END*************************"
        done
}

function get_err_type()
{
        ret=""
        case $1 in
        "0")ret="[log_output_error]";;
        "1")ret="[get_host_failed]";;
        "2")ret="[get_leader_failed]";;
        "3")ret="[non_emptyBlockcaused_viewchange]";;
        "4")ret="[socket_closed]";;
        *) ret="[UNKNOWN]";;
        esac
        echo "$ret"
}

#
FOREARD_MESSAGE_ALAM_PERSEND=50
# 
AVG_SEAL_COUNT=5
# Analysis of Result
function do_log_analyze_statistics_result()
{
        local group_id="${1}"
        local node_dir="${2}"
        msg_total=0
        msg_view_total=0;
        msg_sign_total=0;
        msg_pre_total=0;
        msg_commit_total=0;
        msg_f=0
        msg_sign_f=0;
        msg_view_f=0;
        msg_commit_f=0;
        msg_pre_f=0;
        node_count=$(get_total_consensus_node_count ${group_id})
        # handle with view pre sign commit message.
        for i in "${!view_total[@]}"
        do
                ((msg_total+=${view_total[$i]}))
                ((msg_view_total+=${view_total[$i]}))
        done

        for i in "${!pre_total[@]}"
        do
                ((msg_total+=${pre_total[$i]}))
                ((msg_pre_total+=${pre_total[$i]}))
        done

        for i in "${!sign_total[@]}"
        do
                ((msg_total+=${sign_total[$i]}))
                ((msg_sign_total+=${sign_total[$i]}))
        done

        for i in "${!commit_total[@]}"
        do
                ((msg_total+=${commit_total[$i]}))
                ((msg_commit_total+=${commit_total[$i]}))
        done

        for i in "${!view_f[@]}"
        do
                ((msg_f+=${view_f[$i]}))
                ((msg_view_f+=${view_f[$i]}))
            
        done

        for i in "${!pre_f[@]}"
        do
                ((msg_f+=${pre_f[$i]}))
                ((msg_pre_f+=${pre_f[$i]}))
        done

        for i in "${!sign_f[@]}"
        do
                ((msg_f+=${sign_f[$i]}))
                ((msg_sign_f+=${sign_f[$i]}))
        done

        for i in "${!commit_f[@]}"
        do
                ((msg_f+=${commit_f[$i]}))
                ((msg_commit_f+=${commit_f[$i]}))
        done
	
	if [ "${msg_total}" -ne 0 ];then
        ((per=msg_f*100/msg_total))
           if [[ per -ge FOREARD_MESSAGE_ALAM_PERSEND ]];then
                  alarm "[node:${node_dir}][group:${group_id}] forward message(view_f, pre_f, sign_f, commit_f)=(${msg_view_f}, ${msg_pre_f}, ${msg_sign_f}, ${msg_commit_f}), (view, pre, sign, commit)=(${msg_view_total}, ${msg_pre_total}, ${msg_sign_total}, ${msg_commit_total}) is proportion of too much, total is $msg_total, forward is $msg_f."
           fi
        fi

        total_blk=0
        for i in "${!report[@]}"
        do
             for j in "${report[$i][@]}"
             do
                ((total_blk +=${report[$i][$j]}))
             done
        done

        ((exp_total=node_count*AVG_SEAL_COUNT))

        if [[ $total_blk -ge ${exp_total} ]];then
                avg=$(($total_blk/$node_count))
                err_msg=""
                for ((i=0;i<node_count;++i))
                do
                        count=${report[$i]}
                        if [[ -z $count ]];then
                                count=0
                        fi

                        if [[ $count -le $avg/2 ]];then
                                err_msg=$err_msg" |node$i, seal blk count is $count"
                        fi 
                done

                if [[ ! -z "$err_msg" ]];then
                        alarm "[node:${node_dir}][group:${group_id}] total sealed blk count is $total_blk, node count is ${node_count}, ${err_msg}"
                fi
        fi
}

# show log analyze result.
function do_log_analyze_error_result()
{
        local group="${1}"
        local node_dir="${2}"
        index=0
        if [ ${#err[@]} -gt 0 ];then
            err_msg="[node:${node_dir}] [group:${group}] "
            LOG_ERROR "[node: ${node_dir}][group:${group}]: error information:"
        else
            LOG_INFO "[node:${node_dir}][group:${group}] work normally~"
        fi
        for i in "${!err[@]}"
        do
                err_msg="$err_msg | error.message=$(get_err_type $i), error.count=${err[$i]} "
                ((index+=1))
                echo "error.msg = $(get_err_type $i) , error.count = "${err[$i]}
        done

        if [[ "$err_msg" != "" ]];then
                alarm "[node:${node_dir}][group:${group_id}] ${err_msg}"
                LOG_ERROR "[node:${node_dir}][group:${group_id}] ${err_msg}"
        fi
}

# show log analyze result.
function show_log_analyze_result()
{
        group="${1}"
        # show warning
        LOG_INFO "[group: ${group}] warning message size = ${warning[0]}"
        # view total
        if [ ${#view_total[@]} -gt 0 ];then
            LOG_INFO "[group: ${group}] total view message"
        else
            LOG_INFO "[group: ${group}] total view message = 0"
        fi
        for i in ${!view_total[@]}
        do
                echo "view_req.idx=$i, view_req.count=${view_total[$i]}"
        done
        # direct viewchange
        if [ ${#view_d[@]} -gt 0 ];then
            LOG_INFO "[group: ${group}] direct view message"
        else
            LOG_INFO "[group: ${group}] direct view message = 0"
        fi
        for i in ${!view_d[*]}
        do
                echo "direct_view_req.idx=$i, direct_view_req.count=${view_d[$i]}"
        done

        # forward viewchange
        if [ ${#view_f[@]} -gt 0 ];then
            LOG_INFO "[group: ${group}] forward view message info:"
        else
            LOG_INFO "[group: ${group}] forward view message = 0"
        fi
        for i in ${!view_f[*]}
        do
                 echo "forward_view_req.from=$i, forward_view_req.count=${view_f[$i]}"
        done

        # prepare request
        if [ ${#pre_total[*]} -gt 0 ];then
            LOG_INFO "[group: ${group}] total pre message info:"
        else
            LOG_INFO "[group: ${group}] total pre message = 0"
        fi
        for i in ${!pre_total[*]}
        do
                echo "total_prepare_req.idx=$i, total_prepare_req.count=${pre_total[$i]}"
        done

        # local prepare request
        if [ ${#pre_d[@]} -gt 0 ];then
            LOG_INFO "[group: ${group}] local prepare message info:"
        else
            LOG_INFO "[group: ${group}] local prepare message = 0"
        fi
        for i in ${!pre_d[*]}
        do
                echo "local_prepare_req.idx=$i, local_prepare_req.count=${pre_d[$i]}"
        done

        # forward prepare
        if [ ${#pre_f[@]} -gt 0 ];then
            LOG_INFO "[group: ${group}] forwad prepare message info:"
        else
            LOG_INFO "[group: ${group}] forwad prepare message = 0"
        fi
        for i in ${!pre_f[*]}
        do
                echo "forward_prepare_req.idx=$i, forward_prepare_req.count=${pre_f[$i]}"
        done

        # total sign req
        if [ ${#sign_total[@]} -gt 0 ];then
            LOG_INFO "[group: ${group}] total sign message info:"
        else
            LOG_INFO "[group: ${group}] total sign message = 0"
        fi
        for i in ${!sign_total[*]};do
                echo "total_sign_req.idx=$i, total_sign_req.count=${sign_total[$i]}"
        done

        # direct sign req
        if [ ${#sign_d[@]} -gt 0 ];then
            LOG_INFO "[group: ${group}] direct sign message info:"
        else
            LOG_INFO "[group: ${group}] direct sign message = 0"
        fi
        for i in ${!sign_d[*]}
        do
                echo "direct_sign_req.idx=$i, direct_sign_req.count=${sign_d[$i]}"
        done

        #forward sign req
        if [ ${#sign_f[@]} -gt 0 ];then
            LOG_INFO "[group: ${group}] forward sign message info:"
        else
            LOG_INFO "[group: ${group}] forward sign message = 0"
        fi
        for i in ${!sign_f[*]}
        do
                echo "forward_sign_req.idx=$i, forward_sign_req.count=${sign_f[$i]}"
        done

        # total commit message
        if [ ${#commit_total[@]} -gt 0 ];then
            LOG_INFO "[group: ${group}] total commit message info:"
        else
            LOG_INFO "[group: ${group}] total commit message = 0"
        fi
        for i in ${!commit_total[*]}
        do
                echo "total_commit_req.idx=$i, total_commit_req.count=${commit_total[$i]}"
        done

        # direct commit request
        if [ ${#commit_d[@]} -gt 0 ];then
            LOG_INFO "[group: ${group}] direct commit message info:"
        else
            LOG_INFO "[group: ${group}] direct commit message = 0"
        fi
        for i in ${!commit_d[*]}
        do
                echo "direct_commit_req.idx=$i, direct_commit_req.count=${commit_d[$i]}"
        done

        # forward commit request
        if [ ${#commit_f[@]} -gt 0 ];then
            LOG_INFO "[group: ${group}] forward commit message info:"
        else
            LOG_INFO "[group: ${group}] forward commit message = 0"
        fi
        for i in ${!commit_f[*]}
        do
                echo "forward_commit_req.idx=$i, forward_commit_req.count=${commit_f[$i]}"
        done

        # report message
        if [ ${#report[@]} -gt 0 ];then
            LOG_INFO "[group: ${group}] report message info:"
        else
            LOG_INFO "[group: ${group}] report message = 0"
        fi
        for i in ${!report[*]}
        do
                echo "report.idx=$i, report.count=${report[$i]}"
        done

        # err message result
        if [ ${#err[@]} -gt 0 ];then
            LOG_ERROR "=====[group: ${group}] error message info:====="
        else
            LOG_INFO "[group: ${group}] error message = 0"
        fi
        for i in ${!err[*]}
        do
                LOG_ERROR "error.msg="$(get_err_type $i)", error.count=${err[$i]}"
        done
}

# analyze log file of which content recorded start_time and end_time.
function do_log_analyze_by_duration_time()
{
        nodedir=$1
        #start_time=$2
        #end_time=$3
        LOG_INFO "start_time is $start_time #$(date -d @$start_time +"%Y-%m-%d %H:%M:%S")"
        LOG_INFO "end_time is $end_time #$(date -d @$end_time +"%Y-%m-%d %H:%M:%S")"

        # date -d @1361542596 +"%Y-%m-%d %H:%M:%S"
       start_log="log_"$(date -d @${start_time} +"%Y%m%d%H")".*.log"

        log_start_time=$(date -d @${start_time} +"%Y-%m-%d %H:%M")
        log_end_time=$(date -d @${end_time} +"%Y-%m-%d %H:%M")
        for group in ${group_list[*]};do
            log_dir=$nodedir/log/$start_log
                # start time and end time is different log file, now the max duration is 60 min, so start time and end time is most in two file.
			      LOG_INFO "===== begin parse file:"$nodedir"/log/"$end_log"==========="
            eval $(ls ${log_dir} 2>/dev/null | xargs sed -n "/$log_start_time/,/$log_end_time/p" | awk -v from=${node_idx} -v group_id=${group} -f monitor.awk)
            show_log_analyze_result ${group}
            do_log_analyze_statistics_result ${group} $nodedir
       done

}

# analyze log file of which content recorded during time_point min.
function do_log_analyze_by_time_point()
{
        nodedir=$1
        time_point=$2
        # date -d @1361542596 +"%Y-%m-%d %H:%M:%S"
        
	for log_file in $(ls $nodedir/log/log_$(date -d @${time_point} +"%Y%m%d%H")*);do
		#log_file="log_"$(date -d @${time_point} +"%Y%m%d%H")".log"

        	log_min_time=$(date -d @${time_point} +"%Y-%m-%d %H:%M")

	        LOG_INFO " #log parser, $(date -d @$time_point +"%Y-%m-%d %H:%M:%S")"

	        if [[ ${g_debug} == "true" ]];then
        	        sed -n "/$log_min_time/p" $nodedir/log/$log_file 2>/dev/null > $nodedir/$time_point"_test.log"
        	fi
	        for group in ${group_list[*]};do
        	        LOG_INFO "#parse log $log_file for group:${group}"
               		eval $(sed -n "/$log_min_time/p" $log_file 2>/dev/null | awk -v from=${node_idx} -v group_id=${group} -f monitor.awk)
	                if [[ $? -eq 0 ]];then
        	                do_log_analyze_error_result ${group} ${nodedir}
                	        show_log_analyze_result ${group}
	                fi
        	done
	done
}

# analyze log file.
function do_log_analyze_by_file()
{
        file="${1}"
        if [[ ! -f $file ]];then
                echo " $file is not exist. "
                return
        fi
        IFS_old=${IFS}
        IFS=','
        group_list=(${group_list_str})
        IFS=${IFS_old}
        for group in ${group_list[*]};do
        eval $(awk -v from=${node_idx} -v group_id=${group} -f monitor.awk $file)
        if [[ $? -eq 0 ]];then
                show_log_analyze_result ${group}
        fi
        done
}

# 
function do_all_log_analyze()
{
        for configfile in `ls $dirpath/node*/config.ini`
        do
            nodedir=$(dirname $configfile)
            echo "  "
		    echo "========= do_all_log_analyze: ${nodedir} BEGIN========="
            # check if node work well first, then do log analyze.
		    check_node_work_properly $nodedir
            do_log_analyze_by_duration_time $nodedir $start_time $end_time
		    echo "========= do_all_log_analyze: ${nodedir} END========="
            echo "  "
        done
}

mode="monitor"
log_file=""
duration=10
# default end_time when log analyze
end_time=$(($(date +%s) - 30))
# default start_time when log analyze
start_time=$(($end_time-duration*60))

# help
function help()
{
        echo "Options :"
        echo -e "-s[Recommend]:  send alert to your address"
        echo -e "-m[Optional]:\tfunction, include to monitor and statistics, default is monitor "
        echo -e "-f[Required]:\tlog file to be analyzed"
        echo -e "-o[Required]:\tdirpath"
        echo -e "-p[Optional]:\tname of the monitored program , default is fisco-bcos"
        echo -e "-g[Optional]:\tused in statistics mode, default is 1, specified the group list to be analized"
        echo -e "-d[Optional]:\tlog analyze time range. default : 10(min), it should not bigger than max value : 60(min)"
        echo -e "-r[Recommend]:  setting alert receiver"
        echo -e "-R[Optional]:\trestart node when monitor node failure(default not restart)"
        echo -e "-c[Optional]:\texpected connections, e.g. 3 in the 4-node case, default is 1"
	echo -e "-h:\thelp"
        echo "Usages : "
        echo "   bash  monitor.sh -s yourmail@mail.com -o nodes -r your_name -R -c expected_connections"
        echo "   bash  monitor.sh -s yourmail@mail.com -m statistics -o nodes -r your_name -g group_list"
	echo "Examples : "
        echo "   bash  monitor.sh -s yourmail@mail.com -o nodes -r your_name -R -c 3"
        echo "   bash  monitor.sh -s yourmail@mail.com -m statistics -f node0/log/log_2019021314.log -g 1 2 -r your_name -g 1"
        exit 0
}

function main()
{
while getopts "s:m:f:d:o:g:p:r:c:Rh" option;do
    case $option in
    s) receiver_addr=$OPTARG;;
    m) mode=$OPTARG;;
    f) log_file=$OPTARG;;
    d)
        if [[ $OPTARG -gt 0 && $OPTARG -le 60 ]];then
                duration=$OPTARG
                start_time=$(($end_time-duration*60))
        fi
        ;;
    o) dirpath=$OPTARG;;
    p) program=$OPTARG;;
    r) alert_receiver=$OPTARG;;
    R) restart="true";;
    g) group_list_str=$OPTARG;;
    c) expected_cons=$((OPTARG));;
   
    h) help;;
    esac
done

case $mode in
 monitor)
        check_all_node_work_properly
        ;;
 statistics)
        if [[ -z $log_file ]];then
                do_all_log_analyze  
        else
                do_log_analyze_by_file "$log_file"
        fi
        ;;
 *)
        help
        ;;
esac
}

main "$@"
