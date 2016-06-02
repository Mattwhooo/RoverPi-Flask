var haveEvents = 'ongamepadconnected' in window;
var controllers = {};
var socket = io.connect('http://' + document.domain + ':' + location.port + '/rover');


socket.on('newUser', function(data){
    $.bootstrapGrowl(data + " has joined.", { ele: "body", type: "info", delay: 6000, allow_dismiss: true });
});
socket.on('newController', function(data){
    $.bootstrapGrowl(data + " has connected a controller.", { ele: "body", type: "info", delay: 6000, allow_dismiss: true });
});
socket.on('removeUser', function(data){
    $.bootstrapGrowl(data + " has left.", { ele: "body", type: "info", delay: 6000, allow_dismiss: true });
});
socket.on('removeController', function(data){
    $.bootstrapGrowl(data + " has removed a controller.", { ele: "body", type: "info", delay: 6000, allow_dismiss: true });
});

socket.on('who am i', function(data){
    var person = window.prompt('Who are you?', '');
    socket.emit('broadcast user', person);

});

function connecthandler(e) {
    addgamepad(e.gamepad);
    //showOverlay();
}

function showOverlay(){
    if (typeof controllers[0] !== 'undefined' ){
        $('.overlay').fadeOut();
    }else{
        $('.overlay').fadeIn();
    }
}

function addgamepad(gamepad) {
    controllers[gamepad.index] = gamepad;

    for (var i = 0; i < 4; i++) {
        var p = document.createElement("progress");
        var s = document.createElement("span");
        var d = document.createElement('div');
        s.setAttribute('id', 'axes' + i)
        d.innerText='Axis ' + i;
        p.className = "axis";
        if(i==1 || i==3 || i == 5) {
           p.className = "axis vertical-axis"
        }
        p.setAttribute("max", "2");
        p.setAttribute("value", "1");
        //p.innerHTML = i;

        s.appendChild(p)
        s.appendChild(d)

        document.getElementById('axes').appendChild(s);
    }

    socket.emit('broadcast controller');
    requestAnimationFrame(updateStatus);
}

function disconnecthandler(e) {
    removegamepad(e.gamepad);
    socket.emit('broadcast remove controller');
    //showOverlay();
}

function removegamepad(gamepad) {
    var d = document.getElementById("controller" + gamepad.index);
    document.body.removeChild(d);
    delete controllers[gamepad.index];
}
var oldMessage = ''

var last = new Date().getTime();

function updateStatus() {
    if (!haveEvents) {
        scangamepads();
    }

    var i = 0;
    var j;

    for (j in controllers) {
        var controller = controllers[j];
        if (new Date().getTime() - last > 125){

            if (controller.axes[4] != 0) {
                console.log('horizontal offset')
                var lastHorizontal = new Date().getTime();
                socket.emit('horizontal offset', controller.axes[4])
            }

            if (controller.axes[5] != 0) {
                var lastVertical = new Date().getTime();
                console.log('vertical offset')
                socket.emit('vertical offset', controller.axes[5])
            }
            last = new Date().getTime();
        }


        var d = document.getElementById("controller");
        var message = '';
        var axes = d.getElementsByClassName("axis");
        for (i = 0; i < 4; i++) {
            var a = axes[i];
            a.innerHTML = i + ": " + controller.axes[i].toFixed(4);
            a.setAttribute("value", controller.axes[i] + 1);
            if (controller.axes[i] > 0.1 || controller.axes[i] < -0.1){
                message += i.toString() + '=' + controller.axes[i] + ';';
            }else{
                message += i.toString() + '=0;';
            }

        }
        if(oldMessage != message){
            socket.emit('gamepadUpdate', message);
            oldMessage = message;
        }
    }

    requestAnimationFrame(updateStatus);
}


function scangamepads() {
    var gamepads = navigator.getGamepads ? navigator.getGamepads() : (navigator.webkitGetGamepads ? navigator.webkitGetGamepads() : []);
    for (var i = 0; i < gamepads.length; i++) {
        if (gamepads[i]) {
            if (gamepads[i].index in controllers) {
                controllers[gamepads[i].index] = gamepads[i];
                //showOverlay();
            } else {
                addgamepad(gamepads[i]);
            }
        }
    }
}


window.addEventListener("gamepadconnected", connecthandler);
window.addEventListener("gamepaddisconnected", disconnecthandler);

if (!haveEvents) {
    setInterval(scangamepads, 500);
}
//showOverlay();