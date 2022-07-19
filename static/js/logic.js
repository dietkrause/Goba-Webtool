
function handleData() {
    // list of ids of the divs that contain the checkboxes
      let ids=["B","D","F","H","J","L","N","P","R","T","V","X","Z"];
    // list of ids of the textarea tags that contain the comments linked with the previos ids
      let comments=["C","E","G","I","K","M","O","Q","S","U","W","Y","AA"]
      let data=[]
      var cont=true
      for (var i = 0; i < ids.length; i++) {
        if ( cont == false) {
            break
        }
        let list=[]    
        var checks = document.getElementById(ids[i]).getElementsByTagName("input");
        var text = document.getElementById(comments[i]).value;
        for (var j = 0; j < checks.length; j++) {
                let str = 'input[name=' + "'" + checks[j].name +"'" + "]:checked"
                let chk = document.querySelector(str)
                let nl = list.push(chk) 
            }
        var validation="none"
        let validate=list[0]
        let reject = list[1]
        console.log("validate ->",validate)
        console.log("reject ->",reject)
          if(reject==null && validate != null){
            validation=true;
          }
          else if (validate==null && reject != null) {
            validation=false
          }
          else if (validate==null && reject==null) {
            validation="pending"
          }
          else {
          alert('Please select just one!');
          var cont = false
          break
        }
        let info=[ids[i],validation,text]
        let nl2 = data.push(info)
        }
        let name = document.getElementById("page_title").name
        let nl3 = data.push(name)
        notify=document.querySelector('input[name="notify_user"]:checked')
        if (notify == null){
          let nl4 = data.push(false)
        }
        else {
          let nl4 = data.push(true)
        }
        console.log(data)
        $.ajax({
                url:"/update-client-information",
                type:"POST",
                contentType:"application/json",
                data:JSON.stringify(data)
            })
            document.location.reload()
      }

function btn_handler() {
        var names = $('.prompt').select2('data');
        $.ajax({
            url:"/Processinfo",
            type:"POST",
            contentType:"application/json",
            data:JSON.stringify(names)
        })
        document.location.reload()
    }

function btn_handler_users() {
      var user = $('.prompt').select2('data');
      console.log(user)
      $.ajax({
          url:"/receive-users",
          type:"POST",
          contentType:"application/json",
          data:JSON.stringify(user)
      })
      document.location.reload()
  }

  function btn_handler_clients() {
    var user = $('.prompt').select2('data');
    $.ajax({
        url:"/select-pending",
        type:"POST",
        contentType:"application/json",
        data:JSON.stringify(user)
    })
    document.location.reload()
}

function Redirect(button) {
        var val =button.getAttribute("value");
        console.log(val);
        $.ajax({
          url:"/look-client",
          type:"POST",
          contentType:"application/json",
          data:JSON.stringify(val)
      })
    }