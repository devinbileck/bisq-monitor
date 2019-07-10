$('#first_cat').on('change',function(){

    $.ajax({
        url: "/chart",
        type: "GET",
        contentType: 'charset=UTF-8',
        data: {
            'selected': document.getElementById('plot_type').value
        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('bargraph', data);
        }
    });
})
