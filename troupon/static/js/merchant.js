$(document).ready(function() {

    var button  = $('#m_submit');
    button.attr('disabled', 'disabled');

    var telInput = $('#telephone');
    telInput.intlTelInput({
        initialCountry: 'auto',
        geoIpLookup: function(callback) {
            $.get('http://ipinfo.io', function() {},
                 'jsonp').always(function(resp) {
            var countryCode = (resp && resp.country) ? resp.country : '';
            callback(countryCode);
        });
    },
        utilsScript: '/static/lib/libphonenumber/build/utils.js',
        nationalMode: 'true'
    });

    var errorMsg = $('#error-msg');
    var validMsg = $('#valid-msg');

    var reset = function() {
        telInput.removeClass('error');
        errorMsg.addClass('hide');
        validMsg.addClass('hide');
    };

    // on blur: validate
    telInput.blur(function() {
        reset();
            if ($.trim(telInput.val())) {
            if (telInput.intlTelInput('isValidNumber')) {
              validMsg.removeClass('hide');
            } else {
              telInput.addClass('error');
              errorMsg.removeClass('hide');
            }
        }
    });

    var TokenGenerator = {
        goResend: function (event) {
            var _this = this;
            url = $(this).data('href');
            location.href = url
        },
        enableVerify: function (event) {
            if(this.$tokenField.val().length ===  6){
                this.$verifyButton.removeAttr('disabled');
            } else {
                this.$verifyButton.attr('disabled', 'disabled');
            }
        },
        $tokenField: $('#id_token_name'),
        $verifyButton: $('#id_verify_button'),
        $resendButton: $('#id_resend_button'),
        init: function () {
            this.$verifyButton.attr('disabled', 'disabled');
            this.applyEvents();
        },
        applyEvents: function () {
            this.$resendButton.on('click', this.goResend);
            this.$tokenField.on('keyup', this.enableVerify.bind(this));
        }
    }

    TokenGenerator.init();

    // on keyup / change flag: reset
    telInput.on('keyup change', reset);

        $('form').submit(function() {
        $('#hidden1').val(telInput.intlTelInput('getNumber'));

    });
        $('form :input').change(function() {
            $(this).closest('form').data('changed', true);
            button.removeAttr('disabled');
    });

});