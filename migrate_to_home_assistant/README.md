### How to add DHT11 with NodeMCU to Home Assistant

After I discovered Home Assistant, this repository begun useless. So, in this instruction I show how to add DHT11 with NodeMCU to Home Assistant.

Unlike temperature_monitor_api with FastAPI, for Home Assistant there are another strategy to catch data from sensor. Home Assistant make requests to NodeMCU HTTP-server and read response.

* Upload [./NodeMCU_DHT11_Server/NodeMCU_DHT11_Server.ino](./NodeMCU_DHT11_Server/NodeMCU_DHT11_Server.ino) to NodeMCU.
* Discover what ip address router assign to NodeMCU
* In your Home Assistant `config/configuration.yaml` add sensors:
```yaml
sensor:
  - platform: rest
    unique_id: nodemcu_temperature
    name: nodemcu_temperature
    resource: <node_mcu_ip>/temperature
    value_template: "{{ value }}"
    unit_of_measurement: "°C"

  - platform: rest
    unique_id: nodemcu_humidity
    name: nodemcu_humidity
    resource: <node_mcu_ip>/humidity
    value_template: "{{ value }}"
    unit_of_measurement: '%'
```

* Add two cards to dashboard (click edit dashboard, create empty card and paste):
```yaml
graph: line
type: sensor
entity: sensor.nodemcu_temperature
detail: 2
name: Temperature
```

```yaml
graph: line
type: sensor
entity: sensor.nodemcu_humidity
detail: 2
name: Humidity
```