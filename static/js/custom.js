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



});
