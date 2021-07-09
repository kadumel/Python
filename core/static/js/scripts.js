
 $('#inputLoja2').click(function(){
    this.value = ''
    $('#Lojacomplete').prop('selectedIndex',0)
})

$('#inputGrupo').click(function(){
    this.value = ''
    $('#GrupoComplete').prop('selectedIndex',0)

})

$('#inputGrupo').blur(function(){

    if (this.value != '') {
        var valor = $('#inputGrupo').val()
        $('#SubgrupoComplete').empty()
         $.ajax({
                type:"POST",
                headers: {'X-CSRFToken': csrftoken},
                url: "http://127.0.0.1:8000/filtroSubgrupo",
                data: {grupo: valor},
                success: function(dt){
                    var obj = JSON.parse(dt)
                    obj.forEach(function(o, index){
                          console.log(o)
                          $('#SubgrupoComplete').append('<option>'+o.nmsubgrupo+'</option>' )
                     });
                }
            });
         }
})

$('#inputSubGrupo').click(function(){
    this.value = ''
    $('#SubGrupoComplete').prop('selectedIndex',0)

    if ($('#inputGrupo').val() == ''){
        alert('Selecione um grupo!!!')
    }

})

<!--Modal-->




function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

        var csrftoken = getCookie('csrftoken');

<!-- Consulta os produtos para preenchimento dos valores de acordo com o filtro-->

    $("#consultar").click(function(){

          var movimento = $("#inputTipoM").val();
          var loja = $("#inputLoja2").val();
          var grupo = $("#inputGrupo").val();
          var subgrupo = $("#inputSubGrupo").val();

            console.log("Teste Ajax - "+ csrftoken)
            $.ajax({
                type:"POST",
                headers: {'X-CSRFToken': csrftoken},
                url: "https://ezbi-pannemix.herokuapp.com/filtroMovimento",
                data: {movimento: movimento, loja: loja, grupo: grupo, subgrupo: subgrupo },
                success: function(dt){
                  console.log('Retorno dos dados Pesquisa Dados:' + dt)

                    var obj = JSON.parse(dt)

                    $(".lpTbody tr").remove()
                    obj.forEach(function(o, index){
                          preecheTabela(o.cdproduto, o.nmproduto)

                     });
                }
            });
    });


 $('td:nth-child(1),th:nth-child(1)').hide();

function preecheTabela(cd, nm){

          var corpoTabela = document.querySelector("tbody")

           var linha = document.createElement("tr")
           var codigo = document.createElement("td")
           var nome = document.createElement("td")
           var input = document.createElement("input")
           input.type="number"
           input.id="vlPrd"




           var vlCodigo = document.createTextNode(cd)
           var vlNome = document.createTextNode(nm)

           codigo.appendChild(vlCodigo)
           nome.appendChild(vlNome)

           linha.appendChild(codigo)
           linha.appendChild(nome)
           linha.appendChild(input)

            corpoTabela.appendChild(linha)

            $('#tbInsert td:nth-child(1),th:nth-child(1)').hide();

<!--            input.css({display: "block", margin: "10 auto", background: "red"})-->


}


$("#btnInserir").click(function(){



       produtos = lerTabela()
       cabecalho = lerCabecalho()

        const varStorage = localStorage.getItem("idMovPannemix")
        console.log($('#inputLoja2').val())
        if ( $('#inputLoja2').val() != "") {

              if (varStorage) {

                  $.ajax({
                          type:"POST",
                          headers: {'X-CSRFToken': csrftoken},
                          url: "https://ezbi-pannemix.herokuapp.com/movimento",
                          data: {cab: cabecalho, prod: produtos, flag: varStorage},
                          success: function(dt){

                            console.log("Retorno Insert mov:" + dt)
                          }
                    });

              } else {

                  $.ajax({
                          type:"POST",
                          headers: {'X-CSRFToken': csrftoken},
                          url: "https://ezbi-pannemix.herokuapp.com/movimento",
                          data: {cab: cabecalho, prod: produtos, flag: 0},
                          success: function(dt){

                            console.log("Retorno Insert mov:" + dt)
                            localStorage.setItem('idMovPannemix', dt);

                            $('.rdButton').attr("disabled", true);
                            $('#inputLoja2').attr("disabled", true);


                          }
                    });
                   }

                    $(".lpTbody tr").remove()
                    $('#inputGrupo').val("");
                    $('#inputGrupo').attr("placeholder", "Escolha um grupo...");
                    $('#inputSubGrupo').val("");
                    $('#inputSubGrupo').attr("placeholder", "Escolha um subgrupo...");

              } else {

                  alert("Escolha uma Loja!!!")

              }

});


$('#btnFinalizar').click(function(){

        const varStorage = localStorage.getItem("idMovPannemix")

        $.ajax({
                          type:"POST",
                          headers: {'X-CSRFToken': csrftoken},
                          url: "https://ezbi-pannemix.herokuapp.com/fimMovimento",
                          data: {flag: varStorage},
                          success: function(dt){

        <!--                       Remove o id do item do localstorage    -->
                                   localStorage.removeItem('idMovPannemix')

        <!--                       Habilita o radio button dos movimentos     -->
                                   $('.rdButton').attr("disabled", false);

        <!--                       Habilita o campo loja, limpa o campo e seta o placeholder novamente      -->
                                   $('#inputLoja2').attr("disabled", false);
                                   $('#inputLoja2').val("");
                                   $('#inputLoja2').attr("placeholder", "Escolha uma loja...");

                                   alert("Registro finalizado com sucesso!!!")

                          },
                          error: function(XMLHttpRequest, textStatus, errorThrown){
                                alert("O registro não finalizado, tente novamente!!!");
                            }
                    });




});


function lerCabecalho(){

        dados = {
           movimento : $("input[name='inpTpMovi']:checked").val(),
                loja : $("#inputLoja2").val(),
               grupo : $("#inputGrupo").val(),
            subgrupo : $("#inputSubGrupo").val()
          }


          return JSON.stringify(dados)
}


function lerTabela(){

      var produtos = [];
      var lista = $('tbody');
      var input = $('#vlPrd')

      $(lista).find("tr").each(function(index, tr) {
         produtos.push(JSON.stringify(
                      { "cdProduto": $(tr).find('td:eq(0)').html(),
                        "nmProduto": $(tr).find('td:eq(1)').html(),
                        "valor":     $(tr).find('input:eq(0)').val()
                      }))
      });

    return produtos

}


function checaLocalStorage(){

      console.log("Removendo o Item")
      localStorage.removeItem('itemPannemix')

      if (localStorage.getItem("itemPannemix") === null) {
          console.log("Item não existente")
      }

      console.log("Item Adicionado")
      localStorage.setItem('itemPannemix', 'Daniel');



}
