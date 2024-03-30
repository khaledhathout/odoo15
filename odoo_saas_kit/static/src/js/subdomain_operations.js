odoo.define('odoo_saas_kit.subdomain_operations', function(require) {

    var rpc = require('web.rpc');

    $('.revoke_domain').click(function(ev){
        var answer = confirm("Are You Sure You want to Revoke this domain..?");
        if (answer == true){
            var domain_id = parseInt($(ev.currentTarget).attr('domain_id'));
            rpc.query({
                model: 'custom.domain',
                method: 'revoke_subdomain_call',
                args: [domain_id],
            }).then(function(url){
                location.href = url
            });
        }
    });

    $('#sub_domain_span_1, #add_domain_icon_div').click(function(ev){
        $("#add_custom_domain").modal("toggle");
    });

    $('#btn_add_domain').click(function(ev){
        var contract_id = $('#contract_id').attr('value');
        var domain_name = $('#add_subdomain_name').val();
        rpc.query({
            model: 'custom.domain',
            method: 'add_subdomain_call',
            args: [contract_id, domain_name],
        }).then(function(response){
            if (response.success){
                $("#add_custom_domain").modal("hide");
                location.href = response.msg;
            }else{
                $('#domain_taken_warning').text(response.msg);
                $('#domain_taken_warning').show();
            }
        });
    });
});