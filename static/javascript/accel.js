var x = 0, y = 0,
    vx = 0, vy = 0,
	ax = 0, ay = 0;
	
var sphere = document.getElementById("sphere");

#debug - sanity check
#window.alert("stuff going")

if (window.DeviceOrientationEvent) {
        //window.alert("Device Orientation Event!");
        $("e").innerHTML = "DeviceOrientationEvent";
        window.addEventListener('deviceorientation', function(e) {
            // y-axis - yaw
            var g = e.gamma || 0;
            // x-axis - tilt
            var b = e.beta || 0;
            // z=axis - swivel
            var a = e.alpha || 0;
            // degree north
            var c = e.compassHeading || e.webkitCompassHeading || 0;
            // accuracy in deg
            var accuracy = e.compassAccuracy || e.webkitCompassAccuracy || 0;
            // deviceOrientationHandler(g, b, a, c, accuracy);
            compassData = 'cGamma='+g+';cBeta='+b+';cAlpha='+a+';cHeading='+c+';cAccuracy='+accuracy;
//            socket.emit('compassUpdate', accelData);
//            console.log("gamma:",g," beta:",b," alpha:",a," c:",c," a:",accuracy);
        }, false);

    } else {
        $("e").innerHTML = "NOT SUPPORTED #FAIL";
    }


if (window.DeviceMotionEvent != undefined) {
    // window.alert("a motion event happened");
	window.ondevicemotion = function(e) {
		ax = event.accelerationIncludingGravity.x * 5;
		ay = event.accelerationIncludingGravity.y * 5;
		x = e.accelerationIncludingGravity.x;
		y = e.accelerationIncludingGravity.y;
		z = e.accelerationIncludingGravity.z;
//        console.log('accelX:',e.accelerationIncludingGravity.x)
		if ( e.rotationRate ) {
			rAlpha = e.rotationRate.alpha;
			rBeta = e.rotationRate.beta;
			rGamma = e.rotationRate.gamma;
//			console.log('RALPHA',rAlpha)
			if (rAlpha == null) { rAlpha = 0 }
			if (rBeta == null) { rBeta = 0 }
			if (rGamma == null) { rGamma = 0 }
		}
        //document.write(ax);

    accelData = 'x='+x+';y='+y+';z='+z+';ra='+rAlpha+';rb='+rBeta+';rg='+rGamma
    socket.emit('gyroUpdate', accelData);

    //document.write(ay);
	}

	setInterval( function() {
		var landscapeOrientation = window.innerWidth/window.innerHeight > 1;
		if ( landscapeOrientation) {
			vx = vx + ay;
			vy = vy + ax;
		} else {
			vy = vy - ay;
			vx = vx + ax;
		}
		vx = vx * 0.98;
		vy = vy * 0.98;
		y = parseInt(y + vy / 50);
		x = parseInt(x + vx / 50);

//        console.log(y);
//        console.log(x);
		
		//sphere.style.top = y + "px";
		//sphere.style.left = x + "px";
		
	}, 25);
} 



$(document).ready(function(){
  //window.alert("things afoot!")
  $('#load_video').click(loadVideo);
  $('#show_controller').click(showInput);
});
