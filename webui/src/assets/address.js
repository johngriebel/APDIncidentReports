$(function(){
    $('input.address').each(function(){
        var self = $(this);
    var cmps = $('#' + self.attr('name') + '_components');
    console.log("cmps");
    console.log(cmps);
    var fmtd = $('input[name="' + self.attr('name') + '_formatted"]');
        self.geocomplete({
            details: cmps,
            detailsAttribute: 'data-geo'
        }).change(function(){
            self.data("data", self.geocomplete("details"));
            console.log(self.geocomplete("details"));
            console.log(self.attr("id"))
            if(self.val() != fmtd.val()) {
            var cmp_names = ['country', 'country_code', 'locality', 'postal_code',
                    'route', 'street_number', 'state', 'state_code',
                    'formatted', 'latitude', 'longitude'];
            for(var ii = 0; ii < cmp_names.length; ++ii)
                $('input[name="' + self.attr('name') + '_' + cmp_names[ii] + '"]').val('');
            }
            console.log(self.data("data"));
    });
    });
});