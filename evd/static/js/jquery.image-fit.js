/*
Copyright (C) 2011 by Szymon Danielczyk 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

/*
 * Image Fit JQuery plugin 
 * version 0.0.1
 * 
 *  Usage 
 *  $(seelector).imageFit("fit");
 *  $(seelector).imageFit("pan");
 * 
 */
$.fn.extend({
    imageFit:function(mode) {
      return this.each(function() {
              var $this = $(this);
              var $parent = $this.parent();
              $parent.css({"overflow":"visible"});
              $this.css({width:"100%",height:"auto",margin:0,padding:0,border:"none"});
               
              var imgW = $this.width();
              var imgH = $this.height();
              var contW = $parent.width();
              var contH = $parent.height();
              var imgWHratio = imgW/imgH;
              var contWHratio = contW/contH;
              
              if(mode=="fit"){
                  if(contWHratio>imgWHratio){
                      $this.css({height:"100%",width:"auto"});
                      var marginLeft = Math.floor((contW-$this.width())/2);
                      $this.css({"margin-left":marginLeft});
                  }else if(contWHratio<imgWHratio) {
                      var marginTop = Math.floor((contH-$this.height())/2);
                      $this.css({"margin-top":marginTop});
                  }else{
                    
                  }
              }
              
              if(mode=="pan"){
                  if(contWHratio>imgWHratio){
                       var marginTop = Math.floor((contH-$this.height())/2);
                       $this.css({"margin-top":marginTop});
                       $parent.css({"overflow":"hidden"});
                  }else if(contWHratio<imgWHratio){
                        $this.css({height:"100%",width:"auto"});
                        var marginLeft = Math.floor((contW - $this.width())/2);
                        $this.css({"margin-left":marginLeft});
                        $parent.css({"overflow":"hidden"});
                  }else{
                    
                  }
              }
      });
    }//fitImage end
});