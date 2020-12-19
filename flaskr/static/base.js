function noticeSocketio() {
        
    var noticeSocket = io(
        url="/notice", 
        options={
            forceNew: true,
            reconnectionDelay: 10000
        }
    );
    noticeSocket.on('connect', function() {
        console.log('连接上了');
    });
    noticeSocket.on('disconnect', function() {
        console.log('断开了·');
    });
    noticeSocket.emit(
        'join', 
        ack=function(data){
            console.log(data)
        }
    );

    function addNoticeNum(id) {
        var element = $(id)
        var oldNum = parseInt(element.text())
        if (oldNum == 0){
            element.removeClass("d-none")
        }
        $(element).text(++oldNum)
    }

    noticeSocket.on('application', function(message){
        if(window.Notification && Notification.permission !== "denied") {
            Notification.requestPermission(function(status) {
                var n = new Notification(
                    title='好友申请',
                    option={ body: message['username']+'-'+message['message']}); 
                addNoticeNum("#application-num")
            });
        }
    });
}

(function () {
    window.addEventListener('load', function () {     
        noticeSocketio()
    // end window load
    }, false)
// end (function(){}())
}())
