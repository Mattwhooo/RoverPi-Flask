function showInput(){
  $(this).prop('onclick',null).off('click');

  $('#controller_input').animate({bottom: '0px'}, 500), function(){

  };

  $('#show_controller').animate({bottom: '140px'}, 500, function(){
    $('#showBtn').text('');
    $('#hideBtn').text('Hide Controller Input');
    $('.chevron').removeClass('fa-chevron-up');
    $('.chevron').addClass('fa-chevron-down');
    $('#show_controller').click(hideInput);
  });
}

function hideInput(){
  $(this).prop('onclick',null).off('click');

  $('#controller_input').animate({bottom: '-140px'}, 500, function(){

  });

  $('#show_controller').animate({bottom: '0px'}, 500, function(){

    $('.chevron').addClass('fa-chevron-up');
    $('.chevron').removeClass('fa-chevron-down');
    $('#showBtn').text('Show Controller Input');
    $('#hideBtn').text('');
    $('#show_controller').click(showInput);
  });
}

function loadVideo(){
  var img = document.createElement('img');
  img.setAttribute('src', 'http://' + window.location.hostname + ':8080/stream/video.mjpeg');
  img.setAttribute('class', 'img-responsive');
  img.setAttribute('style', 'height:100%;margin-left:auto;margin-right:auto');
  $('.welcome-message').fadeOut();
  $('#video').replaceWith(img);
  $('#full-screen-video').show()
}
$(document).ready(function(){
  $('#load_video').click(loadVideo);
  $('#show_controller').click(showInput);
  $('#full-screen-video').click(function(){
    if (document.fullscreenEnabled) {
      element = $('.img-responsive')[0]
      requestFullscreen(element);
    }
  });
});


