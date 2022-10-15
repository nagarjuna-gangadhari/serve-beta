$(document).ready(function(){
    $('.group').children('div').click(function(){
          var $children = $(this).children().clone();
          $('#visshymodal .modal-body').append($children).empty();
          $('#visshymodal .modal-body').append($children);
          $('#visshymodal').modal('show');
          $('#visshymodal .modal-body .more').removeClass('hide');
          $('#visshymodal .text ').modal('hide');
          $('#visshymodal .dot').modal('hide');
          $('#visshymodal').find('br').remove();

    });
    $('.slides tr td').click(function(){
          var $children = $(this).children().clone();
          $('#visshymodal .modal-body').append($children).empty();
          $('#visshymodal .modal-body').append($children);
          $('#visshymodal').modal('show');
          $('#visshymodal .modal-body .info').removeClass('hide');
    });
    $('#myCarousel').carousel({
        interval: 5000
    });

});
