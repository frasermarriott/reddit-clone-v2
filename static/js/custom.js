$(function(){

// Prevent spaces from being inputted e.g. for usernames and subreddit names
  $("input.nospace").on({
    keydown: function(e) {
      if (e.which === 32)
        return false;
    },
    change: function() {
      this.value = this.value.replace(/\s/g, "");
    }
  });

// Truncate subreddit descriptions on subreddit list page.
  var minimised_elements = $('p.minimise');

  minimised_elements.each(function(){
    var t = $(this).text();
    if(t.length < 100) return;

    $(this).html(
      t.slice(0,100)+'<span>... </span><a href="#" class="more">Show more</a>'+
      '<span style="display:none;">'+ t.slice(150,t.length)+' <a href="#" class="less">Show less</a></span>'
    );

  });

  $('a.more', minimised_elements).click(function(event){
    event.preventDefault();
    $(this).hide().prev().hide();
    $(this).next().show();
  });

  $('a.less', minimised_elements).click(function(event){
    event.preventDefault();
    $(this).parent().hide().prev().show().prev().show();
  });

// Sidebar toggle

  $("#menu-toggle").click(function(e) {
    e.preventDefault();
    $("#wrapper").toggleClass("toggled");
  });

// Tabs for submit post page (link/text)
  
  $(".nav-tabs a").click(function(){
    $(this).tab('show');
  });

  // select either link or text from url #anchor
  var url = document.location.toString();
  if (url.match('#')) {
      $('.nav-tabs a[href="#' + url.split('#')[1] + '"]').tab('show');
  } 

  // Change anchor hash for page-reload
  $('.nav-tabs a').on('shown.bs.tab', function (e) {
    window.location.hash = e.target.hash;
  });


// comment reply button
  $(".reply-btn").click(function(){
    $(this).closest(".comment-content").find(".reply-form").toggleClass("hidden");
  });

// Votes

  // Upvote
  $('.upvote').click(function() {
    var $this = $(this);
    var votes = $this.nextAll('.votes-number').text();
    var votes = parseInt(votes);

    if ($this.hasClass('upvoted')) {
      $this.removeClass('upvoted').addClass('upvote');
      $this.nextAll('.votes-number').text(votes - 1).removeClass('votes-color-upvoted');
    } else if ($this.hasClass('upvote')) {
      $this.removeClass('upvote').addClass('upvoted');
      $this.nextAll('.votes-number').text(votes + 1).addClass('votes-color-upvoted');
    } else {
      $this.addClass('upvote');
   }
  });

  // Downvote
  $('.downvote').click(function() {
    var $this = $(this);
    var votes = $this.prevAll('.votes-number').text();
    var votes = parseInt(votes);

    if ($this.hasClass('downvoted')) {
      $this.removeClass('downvoted').addClass('downvote');
      $this.prevAll('.votes-number').text(votes + 1).removeClass('votes-color-downvoted');
    } else if ($this.hasClass('downvote')) {
      $this.removeClass('downvote').addClass('downvoted');
      $this.prevAll('.votes-number').text(votes - 1).addClass('votes-color-downvoted');
    } else {
      $this.addClass('upvote');
    }
  });
 

  $('.prev-upvoted').nextAll('.votes-number').addClass('votes-color-upvoted');
  $('.prev-downvoted').prevAll('.votes-number').addClass('votes-color-downvoted');

  // Previously Upvoted
  $('.prev-upvoted').click(function() {
    var $this = $(this);
    var votes = $this.nextAll('.votes-number').text();
    var votes = parseInt(votes);

    if ($this.hasClass('prev-upvoted')) {
      $this.removeClass('prev-upvoted').addClass('upvote');
      $this.nextAll('.votes-number').text(votes - 1).removeClass('votes-color-upvoted');
    } else if ($this.hasClass('upvote')) {
      $this.removeClass('upvote').addClass('prev-upvoted');
      $this.nextAll('.votes-number').text(votes + 1).addClass('votes-color-upvoted');
    } else {
      $this.addClass('upvote');
   }
  });


  // Previously Downvoted
  $('.prev-downvoted').click(function() {
    var $this = $(this);
    var votes = $this.prevAll('.votes-number').text();
    var votes = parseInt(votes);

    if ($this.hasClass('prev-downvoted')) {
      $this.removeClass('prev-downvoted').addClass('downvote');
      $this.prevAll('.votes-number').text(votes + 1).removeClass('votes-color-downvoted');
    } else if ($this.hasClass('downvote')) {
      $this.removeClass('downvote').addClass('prev-downvoted');
      $this.prevAll('.votes-number').text(votes - 1).addClass('votes-color-downvoted');
    } else {
      $this.addClass('upvote');
    }
  });



// Autofocus input within modal popup
  $('.modal').on('shown.bs.modal', function() {
    $(this).find('[autofocus]').focus();
  }); 
  

// Submit form when confirm delete button is clicked in modal popup
  $('#confirm-delete-post').click(function(){
    $('#deletePost').submit();
  });


// Set thumbnails
  $(".sub-list-link").filter(function() {
    url = $(this).attr('href');
    //console.log(url);

    var extension = url.substr( (url.lastIndexOf('.') +1) );
    switch(extension) {
      case 'jpg':
      case 'jpeg':
      case 'png':
        $(this).parent().find('.image-toggler').removeClass('hidden');
        $(this).parent().children().find('.image-toggle').removeClass('hidden');
      break;
      default:
        $(this).parent().children().find('.link-thumb').addClass('default-thumb'); 

    }


    // check for youtube links

    var regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]{11,11}).*/;
    var match = url.match(regExp);
    if (match){ 
      if (match.length >= 2){
        youtube_id = match[2]
        youtube_thumb = "url(https://img.youtube.com/vi/" + youtube_id + "/0.jpg)"
        embed_link = "https://www.youtube.com/embed/" + youtube_id

        $(this).parent().children().find('.link-thumb').removeClass('default-thumb').css({'background-image' : youtube_thumb, 'background-size' : '177%'});
        $(this).parent().find('.youtube-toggler').removeClass('hidden');
        $(this).parent().children().find('.youtube-toggle').removeClass('hidden');
        //$(this).parent().children().find('.youtube-toggle').addClass('isyt');
        $(this).parent().children().find('iframe').attr('src',embed_link);
        $(this).parent().children().find('.link-thumb').children().css({'background-image' : 'url("http://i.imgur.com/MfoMU0Y.png")', 'background-repeat' : 'no-repeat', 'background-position' : '50% 50%', 'background-size' : '23px'});
      }
    }


    // Add default image thumbnail for imgur links that do not end with .jpg/jpeg/png
    var imgurCheck = /^.*(imgur\.com\/[a-zA-Z0-9]{6,8})(?!\.jpg|\.jpeg|\.png)(?:[^a-zA-Z0-9]|$).*/;
    var imgurMatch = url.match(imgurCheck);
    if (imgurMatch){
      //console.log(imgurMatch);
      $(this).parent().children().find('.link-thumb').addClass('default-img-thumb');
    }


    // Check for non-direct imgur links and append .jpg file extension so that thumbnails display correctly
    var imgurCheckDirectLink = /^.*(imgur\.com\/[a-zA-Z0-9]{6,8})(?!\.jpg|\.jpeg|\.png|\.gif|\.gifv)(?:[^a-zA-Z0-9]|$).*/;
    var imgurMatchDirectLink = url.match(imgurCheckDirectLink);
    if (imgurMatchDirectLink){
 
      fixedUrl = url + ".jpg"
      fixedUrlCSS = "url(" + url + ".jpg)"

      $(this).parent().children().find('.link-thumb').removeClass('default-thumb default-img-thumb').css('background-image', fixedUrlCSS);
      $(this).parent().find('.image-toggler-link-fix').removeClass('hidden');
      $(this).parent().find('.img-responsive').attr('src', fixedUrl);

    }


    // Check if link is imgur album
    var imgurAlbumCheck = /^.*(imgur\.com\/a\/(.*?)(?:[#\/].*|$))/;
    var imgurAlbumMatch = url.match(imgurAlbumCheck);
    if (imgurAlbumMatch){

      var albumUrlApi = "https://api.imgur.com/3/album/"+imgurAlbumMatch[2];
     
      // Get album cover image using imgur api
      $.ajax({
        type: "GET",
        url: albumUrlApi,
        dataType: "json",
        beforeSend: function(xhr) {
          xhr.setRequestHeader('Authorization', 'Client-ID 54da2a43d02bef3');
        },
        context: this,
        success: function(data) {
          //console.log(data.data.cover);
          albumCoverId = data.data.cover;
          albumCoverUrl = "url(https://imgur.com/" + albumCoverId + ".jpg)"

          console.log(albumCoverUrl);
          $(this).parent().children().find('.link-thumb').removeClass('default-thumb').css({'background-image' : albumCoverUrl});
          $(this).parent().find('.album-button').removeClass('hidden');
        }
      });
    }

    
  
  });


  // Media toggle buttons
  $('.youtube-toggler').click(function() {
      $(this).siblings('.youtube-toggle').toggleClass('hidden');
  });

  $('.image-toggler').click(function() {
      $(this).siblings('.image-toggle').toggleClass('hidden');
  });

  $('.image-toggler-link-fix').click(function() {
      $(this).siblings('.image-toggle-link-fix').toggleClass('hidden');
  });

  
 /* $('.toggle-all').click(function() {
      $('.isyt').toggleClass('hidden');
  });
*/


});
