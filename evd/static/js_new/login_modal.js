$('.form').find('input, textarea').on('keyup blur focus', function(e) {

    var $this = $(this),
        label = $this.prev('label');

    if (e.type === 'keyup') {
        if ($this.val() === '') {
            label.removeClass('active highlight');
        } else {
            label.addClass('active highlight');
        }
    } else if (e.type === 'blur') {
        if ($this.val() === '') {
            label.removeClass('active highlight');
        } else {
            label.removeClass('highlight');
        }
    } else if (e.type === 'focus') {

        if ($this.val() === '') {
            label.removeClass('highlight');
        } else if ($this.val() !== '') {
            label.addClass('highlight');
        }
    }

});

$('.tab a').on('click', function(e) {

    e.preventDefault();

    $(this).parent().addClass('active');
    $(this).parent().siblings().removeClass('active');

    target = $(this).attr('href');

    $('.tab-content > div').not(target).hide();

    $(target).fadeIn(600);

});
$('.already').on('click', function() {
    $('#buffer').html('');
    $("#current-form-desc").removeClass("alert alert-success alert-danger");
    $('#current-form-desc').html('');
    $('.sp').removeClass('active');
    $('.lg').addClass('active');
    $('#signup').hide();
    $('#login').show();
    window.form_status = "login";

});
$('.not_already').on('click', function() {
    $("#current-form-desc").removeClass("alert alert-success alert-danger");
    $('#current-form-desc').html('');
    $('#buffer').removeClass("alert alert-danger");
    $('#buffer').html('');
    $('.lg').removeClass('active');
    $('.sp').addClass('active');
    $('#login').hide();
    $('#signup').show();
    window.form_status = "signup";

});
/*$('.carousel').carousel({
    interval: false
});*/
$('.carousel-control.left').click(function() {
    $('#quote-carousel').carousel('prev');
});

$('.carousel-control.right').click(function() {
    $('#quote-carousel').carousel('next');
});
$('.carousel-control.left').click(function() {
    $('#quote-carous').carousel('prev');
});

$('.carousel-control.right').click(function() {
    $('#quote-carous').carousel('next');
});
$('.carousel-control.left').click(function() {
    $('#quote-carouse').carousel('prev');
});

$('.carousel-control.right').click(function() {
    $('#quote-carouse').carousel('next');
});
//volunteer page login
//var url      = window.location.href;
//if(url == "http://dev.evidyaloka.org:9004/?show_popup=true&type=Login"){
/*$('#buffer').html('');
$('#current-form-desc').html('');
$('.sp').removeClass('active');
$('.lg').addClass('active');
$('#signup').hide();
$('#login').show();
window.form_status = "login";*/
//window.location.href= "http://dev.evidyaloka.org:9004/?show_popup=true&type=Login#";
//window.history.pushState("", "", '/loginform');
//$("#login-modal").modal('show');
//}

// change content according to click; stop iframe video when modal close
$(".video0").on("click", function() {
    var video_url = "https://www.youtube.com/embed/h2bbbAC_IqU?autoplay=0";
    $("#playerId").attr("src", video_url);
});
$(".video1").on("click", function() {
    //var video_url = "http://www.youtube.com/embed/XVRqXhwcPr8?list=PLbdxk95Fm6YyzIv5Yp_389XPJ33E9CKm5";
    var video_url = "https://www.youtube.com/embed/THyfdA8rttQ?list=PLbdxk95Fm6YyzIv5Yp_389XPJ33E9CKm5";
    $("#playerId").attr("src", video_url);
});
$(".video2").on("click", function() {
    //var video_url = "http://www.youtube.com/embed/ErrFGOX7Vac?list=PLbdxk95Fm6YyzIv5Yp_389XPJ33E9CKm5";
    var video_url = "https://www.youtube.com/embed/R2yTQRpiV0E";
    $("#playerId").attr("src", video_url);
});
$(".video3").on("click", function() {
    //var video_url = "http://www.youtube.com/embed/THyfdA8rttQ?list=PLbdxk95Fm6YyzIv5Yp_389XPJ33E9CKm5";
    var video_url = "https://www.youtube.com/embed/fkApenLZE8w";
    $("#playerId").attr("src", video_url);
});
$("html").on("click", function() {
    if ($('#Modal_evd').css('display') == 'block') {
        console.log("out");
        var video = $("#playerId").attr("src");
        $("#playerId").attr("src", "");
        $("#playerId").attr("src", video);
    }
});

//logout badge
/*$(window).scroll(function() {
    if ($(this).scrollTop() == 0) {
        $(".lgout").css({"color":"white","top":"-60px "});
    }
    else{
        $(".lgout").css({"color":"black","top":"-30px"});
    }
});*/

//details of team: modal

$(".detail_modal a").css("cursor", "pointer");
$(".detail_modal").on("click", "a", function() {
    var get_id = $(this).attr("id");
    var img_src = $(this).closest('figure').find('img').attr('src');
    var t = "Trustee";
    var a = "Advisor";

    console.log(img_src);
    $("#detail_img").attr("src", img_src);
    switch (get_id) {
        case '1':
            $("#name").html("Vishy Thiagarjan");
            $("#designation").html("Trustee/Chairman");
            $("#detailed").html("An engineer from BITS, Pilani, Vishy has more than fifteen years of experience in Mobile, Internet and Telecommunications technologies. He is currently the VP, Device Software at Veveo India (P) Ltd, and prior to that, he was with Motorola, and Winphoria Networks. Vishy strongly believes that educating a child is the best way to create responsible individuals who would further create a better world, and the opportunity to use technology to provide quality education at eVidyaloka is a step towards that dream.");
            break;
        case '2':
            $("#name").html("Ravichandran V");
            $("#designation").html(t);
            $("#detailed").html("An investment banker who moved to Shared Services and was the Head of HP's Global Business Services before moving to Early Childhood Care. Currently, Ravi is with Floretz Academy that is into Montessori schooling for children in the age group of 2 to 6 years in Bangalore, India. In the past, Ravi held various positions, including Sr. VP at HP Global Business Services, Managing Director - India at ANZ Operations & Technology Pt Ltd. and the Vice President, Bank Muscat.");
            break;
        case '3':
            $("#name").html("Venkat Sriraman");
            $("#designation").html("Co-Founder/ Trustee");
            $("#detailed").html("An engineering graduate from BITS Pilani (Class of '95), Venkat has held various engineering positions in the field of Software Product and IT Application Development in companies like Aditi, Citigroup, Honeywell, Microsoft and Dell. Venkat is a passionate technologist who is excited about applying technology to solve chronic social challenges of India, and eVidyaloka is a dream to be realized in that direction, in the form of a social enterprise. For him, the move from a corporate job to the development sector is a conscious profession change and Venkat believes in applying the professional competencies gained towards the execution of a larger social initiative.");
            break;
        case '4':
            $("#name").html("V.Ramkumar");
            $("#designation").html(t);
            $("#detailed").html("A management consultant by profession, Ram is presently a Senior Partner at Cedar, a global management consulting firm, and had earlier worked with PwC. He is a postgraduate in Management from BITS Pilani and has completed his executive education programs at INSEAD and Harvard. With firm conviction that education is the panacea for sustained growth of a society, Ram brings his experience of formulating and implementing strategy for global clients, in the institutional building of eVidyaloka, and promulgating the philosophy of rural education.");
            break;
        case '5':
            $("#name").html("Rizwan Tayaballi");
            $("#designation").html(a);
            $("#detailed").html("Rizwan Tayabali is the Director of the UK-based impact and scaling consultancy, Social Effect and joint CEO of Make A Difference, India. He has worked with and advised more than 150 non-profits and social enterprises in 25 countries around the world. Rizwan has also worked with some of the UK's top finance and retail companies as a management consultant, and thus has deep experience of both the commercial and social sectors. He is on the board of various international non-profit organizations and has spoken on social change at a number of universities including the University of Oxford, UEA and INSEAD.");
            break;
        case '6':
            $("#name").html("Vyjayanthi Sankar");
            $("#designation").html(a);
            $("#detailed").html("An expert in Education, Assessment and Management, Vyjayanthi’s clients include the Brookings Institution, The World Bank, UNICEF, National and State Governments, several NGOs and CSR. Her current research is on building regional learning assessment for South Asia while she supports UN’s Learning Metric Task Force by strengthening capacity for educational assessments in the region. In 2013-14, Vyjayanthi was awarded the prestigious Fulbright Humphrey Fellowship by the US Congress and spent the year in Penn State University for her academic work, and at The World Bank in Washington DC. Prior to her Fulbright Fellowship, Vyjayanthi was part of the start-up team in Educational Initiatives (EI) as the Vice President since 2003, and founded its Large Scale Assessment Division and built it to become the leading assessment provider in South Asia.");
            break;
        case '7':
            $("#name").html("Venkat Sriraman");
            $("#designation").html("Executive Director");
            $("#detailed").html("An Engineering graduate from BITS, Pilani ( Class of '95) has held various engineering positions in the field of software product and IT application development in companies like Aditi, Citigroup, Honeywell, Microsoft and Dell.A passionate technologist, who gets excited about applying technology to solve chronic social challenges of India and eVidyaloka is a dream, to be realized in that direction, in the form of a social enterprise. For him, the move from a corporate job to the development sector is a profession change and believes in applying the professional competencies gained, towards the execution of a larger social initiative.");
            break;
        case '8':
            $("#name").html("Kripa");
            $("#designation").html("Program Manager - Operations");
            $("#detailed").html("A graduate from UDCT, Mumbai and a post graduate from IIT, Kanpur (2010 Batch); she has been into Financial Analytics for 3 years before deciding to switch her career path from corporate to development sector. She has been an enthusiastic and zealous contributor in various NGOs before like Prayas, Akshaya Patra,Teach for India and Dream a Dream. A passionate teacher at heart, she believes, education plays an integral role in shaping and helping a nation grow. She brings with her an enriched experience in field of teacher training, people management and an eagerness to articulate, design and implem ent new ideas to enhance effective learning in students from Rural India. Outside eVidyaloka, she is an ardent photographer and loves to travel and capture the scenic beauty and vibrant moments.");
            break;
        case '9':
            $("#name").html("Sugantha");
            $("#designation").html("Curriculum Manager");
            $("#detailed").html("I am, Sugantha Rajan, associated with eVidyaloka before it was established as a full fledged NGO. In the past I had volunteered as a Teacher for TamilNadu centres. Presently I play the role of Curriculum Coordinator across all centers of eVidyaloka. I hold a Master's degree in Software Systems from BITS Pilani (BE in ECE from Coimbatore), mother of 2 kids, had worked in IT companies for 15+ years in US (initial 2 years from India). My family relocated to India this year. I am excited to be a part of this journey towards helping students in rural areas. I am proud to sh are that I am also a current teacher volunteer for Maths subject in Tamil Nadu centre.");
            break;
        case '10':
            $("#name").html("Venkata Praneeth");
            $("#designation").html("IT Developer");
            $("#detailed").html("The GEEK and our Silent Killer(Popularly known as SK). A B.tech in the stream of Computer Science, graduated in the year 2012 and pursuing his M Tech (Computer Science). His words, \"I am glad, i joined eVidyaloka, where i got an oppourtunity to build my career in IT( Information Technology ) as well as associating to a reputed social organization.\"");
            break;
        case '11':
            $("#name").html("Gayathri Ramesh");
            $("#designation").html("Ops Manager(TN)");
            $("#detailed").html("I am Smt.Gayathri Ramesh, a complete homemaker whose world goes around my family alone. I have been following eVidyal oka since its inception in all its activities. I have always looked upon the founders as my inspiration to do something not just for monetary c ause. After I felt that my kids are less dependent on me I began to think if I'm capable of doing something else on a positive note. I signed u p one fine morning into eVidyaloka after confirming that I need not teach or develop lesson plans, which have never been my force. I love organizing and managing things and hence made an entry into eVidyaloka as one of its Admin with a pinch of fear. I am a perfectionist and love challenges. I strive to face them and succeed too. Thus began my journey 2 years ago and this is my life now. I'm possessed about my center, the children there and the team that runs with me. We see our own world at the center .I don't imagine a day without eVidyaloka which has fulfilled my passion for talking. I don't describe my role at eVidyaloka as something driven by passion or for the sake of service or something to give back to the society but it is my strong feeling that eveiry child deserves the same platform of learning and not deprived of the exposure just because they belong to the rural set up.");
            break;
        case '12':
            $("#name").html("Nikitha Madan");
            $("#designation").html("Ops Coordinator(AP)");
            $("#detailed").html("I had completed my MCA in Coimbatore.Right now settled in Chennai. After my studies I started my career as a teacher in a small school. Teaching kids is my passion. Going way beyond teaching and sharing my knowledge, to bring out the subject to life in ways students will always remember. Volunteering gives us the opportunity to learn about ourselves, to learn about those around us. It is a way to satisfy that need to directly help and change someone’s life. \" Ask not what your country can do for you, ask what you can do for your country.\"");
            break;
        case '13':
            $("#name").html("Deepika Begur");
            $("#designation").html("Assistant Manager");
            $("#detailed").html("Deepika is a post graduate in Bio technology.A Kannadiga, born and brought up in Ananthpur, AP, traces back her drive towards larger societal help to her school and college days. Someone who is passionate about imparting life skills at early stages of student life and prepare them up as emotionally strong individuals as they enter the society. Had worked in a Biotech company briefly, before shifting to the social space with YouthForSeva. And now at eVidyaloka - An empowered, enabling and congenial cultured work place is what keeps her going in realizing her dream of establishing her own NGO down the line.");
            break;
        case '14':
            $("#name").html("Pratima Chattopadhyay");
            $("#designation").html("Manager - Class Delivery");
            $("#detailed").html("I am Pratima based out of Bangalore.I have been working in the e-learning industry for the past eight years. I am very glad to be a part of eVidyaloka, as it gives me an opportunity to do what I always wanted to do- use my skills for those who need it. At eVidyaloka I feel I can use my e-learning experience for educating the kids in villages. I also love travelling and am very enthusiastic about food.");
            break;
        case '15':
            $("#name").html("Rishi Mazumdar");
            $("#designation").html("Program Manager");
            $("#detailed").html("Rishi has a total experience of close to 12 years.He started his career as a Computer Science Teacher in Lucknow (his hometown). Later he moved to the corporate sector, and worked with Companies like IBM Global Services and Dell Inc. While he was with Dell, he worked in functions like Software Engineering, Operations, Training and Development, Process Engineering and Analytics. After spending a considerable amount of time with corporates, he got an opportunity to work with Azim Premji Foundation, where he was program managing their field institute operations. In his most recent role, he was building the Operations unit of a health startup. He is passionate about technology and education and how the same could be amalgamated to create an affordable education model for the nation. His hobbies include photography, travelling, running, cycling and trekking. He has a Student Pilot Certification in Paragliding.");
            break;
        case '19':
            $("#name").html("Dhathri Potla");
            $("#designation").html("Admin Pesarlanka");
            $("#detailed").html("She has been associated with eVidyaloka since 3 yrs now and it has been an amazing experience so far. She says that \"This volunteering opportunity is no more \"volunteering\" as it has been part and parcel of my life. It not only gives me the satisfaction of serving the society, but also gives me lot of confidence and helps me build and enhance the skills that int turn help my back at my work.\" Out of eVidyaloka she work for Microsoft in operations, application support and also have a great passion for yoga. She likes to plan everything and also always aim to be a perfectionist. So now you know that she was busy with, when neither she is at office or executing eVidyaloka activities. ");
            break;
        case '20':
            $("#name").html("Geetha Viswanathan");
            $("#designation").html("Admin Udnabad");
            $("#detailed").html("I am a homemaker with two grown daughters.Now that I have more time to myself, I was looking for something personally fulfiing. my association with Evidyaloka has given me that and more. Helping with the education of such keen kids and working with such willing teachers is agret experience. I am glad to be a part of this growing family.");
            break;
        case '21':
            $("#name").html("Rini Jose");
            $("#designation").html("Charchgura Hira and Cahrchgura Moti Centre Admin");
            $("#detailed").html("A full time homemaker who stumbled on evidyaloka while searching net for something to her free time to productive use.Hope this Journey with evidyaloka will be the most memorable one.");
            break;
        case '16':
            $("#name").html("Ashwini Valimbe");
            $("#designation").html("Shitalpur Admin");
            $("#detailed").html("I am a Doctor working into health technology, mother of a 14year old son.Transformed India is my dream and I embarked on this journey with Evidyaloka which gave me an opportunity to partcipate in disseminating quality education.I look forward to give more time to this and develop a health education program for the school children in future.");
            break;
        case '17':
            $("#name").html("Rama Sudhakar N");
            $("#designation").html("Vamakuntla Centre Admin");
            $("#detailed").html("An IT professional working with TCS in 24/7 shifts to support Microsoft network. A person, who believes only education/literacy can change the standards and fate of a country. Always intended to do something to the society and found eVidyaloka almost close to my thoughts. A voluntary teacher in a local government school. A true lover of teaching");
            break;
        case '18':
            $("#name").html("Balan Varadarajan");
            $("#designation").html("Bero Hira and Bero Moti centre Admin");
            $("#detailed").html("I am 64 years and semi retired now. Worked mostly with Multinational companies like Samsung , Mentergy , Gilat Satellite etc. iBasic Qualification : Graduate.Expertise in Sales & Marketing.Wife is an Author.");
            break;

        case '22':
            $("#name").html("Rini Jose");
            $("#designation").html("Assistant Manager: Volunteer Engagement");
            $("#detailed").html("A commerce graduate with a post graduation in business administration. Started off career in finance field but personal reasons brought her to a little village in the state of Punjab with ample time to find out a fulfilling opportunity and landed in eVidyaloka away from the world of finance right into volunteer engagement.  There on it has been a truly fulfilling and satisfying journey connecting from a village helping kids in another village connect to their teachers. eVidyaloka brought back life to this homemaker who otherwise would have been held up in a Indian home-style life in a rural Indian village.");
            break;
        case '23':
            $("#name").html("D.G,  Nagaraju");
            $("#designation").html("Manager – Administration");
            $("#detailed").html("Completed my graduation 2013 in periyar university distance education. Worked for in aviation engineering department as a store officer in AIE DECCAN, KINGFISHER AIRLINES PVT and GMR AEROTECH LTD Hyderabad. To become a member of professionally managed organization that provides challenging opportunities where I can utilize my skills and contribute effectively to the success of the Organization. Interested in music ,traveling");
            break;
        case '24':
            $("#name").html("Sarbari Ghosh");
            $("#designation").html("Assistant Manager – Class delivery (West Bengal Ops)");
            $("#detailed").html("Sarbari is a teacher with a Masters degree in English Literature and extensive experience of teaching English in various schools in Kolkata and Mumbai. With teaching being her first love, she is committed to an India where every child in every village has access to education and is empowered to build a better future. Apart from teaching, Sarbari is passionate about food, history, travelling and books.");
            break;
        case '25':
            $("#name").html("Shweta Narayanan");
            $("#designation").html("Donor Relations Manager");
            $("#detailed").html("A post graduate in Social Work from Tata Institute of Social Sciences, she has worked with several NGOs, on community based conservation methods, natural resource management, watershed development, sustainable tourism and policy analysis. She has also worked with UNIDO's International Technology Center for building capacity of small and medium manufacturing enterprises and on Goldman Sachs employee volunteering initiative. She is excited to be part of this educational startup that makes quality education accessible, to children in rural areas, by leveraging technology.");
            break;
        case '26':
            $("#name").html("Avanthi Ashwini");
            $("#designation").html("");
            $("#detailed").html("Post graduate from Bangalore University 2008 batch, has held various social service position in the field of Mental Health, Child Guidance, Health & hygiene, Counselling etc., Worked with RAKUM- Organisation,  FDS, NIPCCD, St. John’s Research Institute, Association for Mentally Challenged- NIMHANS. Has a zeal in social work with a set of core ideas. Was an ardent fan of  eVidyaloka which strives to bring out  new smiles to rural Government School kids. I believe that children are like wet cement, as much as we carve them, they will mould themselves a good sculpture and becomes an ever lasting impression.");
            break;
        case '27':
            $("#name").html("Brinda");
            $("#designation").html("Chief Executive Office");
            $("#detailed").html("25 Year of experience across technology, financial services and social sector, through leadership roles in Capgemini, Hewlett Packard & ANZ.\
                        Rural educator in remote areas like the Himalayan Region. \
                        Postgraduate in Computer Science and a Certified Coach and Positive Psychology Practitioner. \
                        Believes that education is not preparation for life but life itself.");
            break;
        case '28':
            $("#name").html("Prof V K");
            $("#designation").html("Chief Patron");
            $("#detailed").html("");
            break;
    }
});


$(document).ready(function() {
    $(".modal-backdrop, #vid_modal .close, #vid_modal .btn").click(function() {
        $("#vid_modal iframe").attr("src", $("#vid_modal iframe").attr("src"));
    });

    //show login modal on direct urls
    if (window.location.href.indexOf("&show_popup=True") === -1) {
        if (window.location.href.indexOf("?next=") > -1) {
            var hash_value = window.location.hash;
            if (hash_value !== null) {
                base_url = window.location.href.replace(hash_value, "")
                window.location.href = base_url + "&show_popup=True" + hash_value;
            } else {
                window.location.href += "&show_popup=True";
            }
        }
    }
});