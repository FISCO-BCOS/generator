BEGIN { 
    # Add to do
    FS="/"
} 

{
    if( $0 ~ /error/ )
        err[0]++ ;
    else if($0 ~ /Host is gone/)
        err[1]++ ;
    else if( $0 ~ /Get leader failed/ && match($0, group_id)) 
        err[2]++ ;
    else if( $0 ~ /ViewChangeWarning/ && match($0, group_id))
        err[3]++ ;
    else if( $0 ~ /.*ssl socket.*close/ )
        err[4]++ ;
    else if ( $0 ~ /p:.*Report.*Idx/ && match($0, group_id)) {
        match($0,/Idx=([0-9]+)/,idx);
        report[idx[1]]++;
    }
    else if ( $0 ~ /p:.*handleViewChangeMsg Succ/ && match($0, group_id)) {
        match($0,/GenIdx=([0-9]+)/,idx);
        view_total[idx[1]]++
        if ( idx_view == from ) {
            view_d[idx[1]]++
        } else {
            view_f[idx[1]]++
        }
    }
    else if ( $0 ~ /p:.*handleSignMsg Succ/ && match($0, group_id)) {
        match($0,/GenIdx=([0-9]+)/,idx);
        sign_total[idx[1]]++
        if ( idx_sig == from ) {
            sign_d[idx[1]]++
        } else {
            sign_f[idx[1]]++
        }
    }
    else if ( $0 ~ /p:.*handlePrepareMsg Succ/ && match($0, group_id)) {
        match($0,/nodeIdx=([0-9]+)/,idx);
        pre_total[idx[1]]++
        if ( idx[1] == from ) {
            pre_d[idx[1]]++
        } else {
            pre_f[idx[1]]++
        }
    }
    else if ( $0 ~ /p.*handleCommitMsg Succ/ && match($0, group_id)) {
        match($0,/GenIdx=([0-9]+)/,idx);
        commit_total[idx[1]]++
        if ( idx[1] == from ) {
            commit_d[idx[1]]++
        } else {
            commit_f[idx[1]]++
        }
    }
    else if ( $0 ~ /warning/ && match($0, group_id)) {
        warning[0]++
} 
}

END { 
    # err message result
    for (k in err) {
        print "err["k"]="err[k]
    }

    # report blk result
    for (k in report) {
        print "report["k"]="report[k]
    }

    # view message
    for (k in view_total) {
        print "view_total["k"]="view_total[k]
    }  

    # direct view message
    for(k in view_d){
        print "view_d["k"]="view_d[k]
    }


    # forward view message
    for(k in view_f){
        print "view_f["k"]="view_f[k]
    }

    # pre
    for(k in pre_total){
        print "pre_total["k"]="pre_total[k]
    }

    # direct pre message
    for(k in pre_d){
        print "pre_d["k"]="pre_d[k]
    }

    # forward view message
    for(k in pre_f){
        print "pre_f["k"]="pre_f[k]
    }

    # sign
    for (k in sign_total) {
        print "sign_total["k"]="sign_total[k]
    }


    # direct sign message
    for(k in sign_d){
         print "sign_d["k"]="sign_d[k]
    }

    # forward view message
    for(k in sign_f){
        print "sign_f["k"]="sign_f[k]
    }

    # commit
    for(k in commit_total){
        print "commit_total["k"]="commit_total[k]
    }

    # direct commit message
    for(k in commit_d){
        print "commit_d["k"]="commit_d[k]
    }

    # forward commit message
    for(k in commit_f){
        print "commit_f["k"]="commit_f[k]
    }
    print "warning["0"]="warning[0]
}
