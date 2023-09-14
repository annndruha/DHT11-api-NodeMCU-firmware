async function fetchJSON(link) {
    const response = await fetch(link)
    return response.json()
}


async function get_all_data(base_config){
    return fetchJSON("/list_devices").then(devices => {
        let promises = []
        for (let device of devices['devices']){
            promises.push(fetchJSON("/measurements_chart_js?device_name=" + device["device_name"]))
        }
        return Promise.all(promises).then(function handleData(all_data) {
            temp_plot_config = structuredClone(base_config)
            hum_plot_config = structuredClone(base_config)
            for (let i=0; i < all_data.length; i++){
                label = devices['devices'][i]["device_name"]
                temp_plot_config['data']['datasets'].push({"label":label, "data": all_data[i]["temperatures"]})
                hum_plot_config['data']['datasets'].push({"label":label, "data": all_data[i]["humiditys"]})
            }
            return [temp_plot_config, hum_plot_config]
        })
    })
}


$.getJSON("./static/plotter.json", function(base_config) {
       console.log(base_config)
       get_all_data(base_config).then(config => {
            plot_temp = document.createElement('canvas')
            plot_temp.id = 'chart_temperature'
            plot_temp.className = "flex-item"
            plot_temp.style = "max-width: 45%; max-height: 500px; padding: 20px;"
            document.getElementById('charts').append(plot_temp)

            temp_plot_config = config[0]
            temp_plot_config['options']['scales']['y']['title']['text'] = "Temperature (°C)"
            let chart1 = new Chart(document.getElementById('chart_temperature'), temp_plot_config)

            plot_hum = document.createElement('canvas')
            plot_hum.id = 'chart_humidity'
            plot_hum.className = "flex-item"
            plot_hum.style = "max-width: 45%; max-height: 500px; padding: 20px;"
            document.getElementById('charts').append(plot_hum)

            hum_plot_config = config[1]
            hum_plot_config['options']['scales']['y']['title']['text'] = "Humidity (%)"
            let chart2 = new Chart(document.getElementById('chart_humidity'), hum_plot_config)

            load = document.getElementById('loading')
            load.remove()
       })
})
