/* src/main.js */
import Aurelia, { Registration } from 'aurelia'
import { RouterConfiguration } from '@aurelia/router'
import { MyApp } from './my-app'
import { IHttpClient, HttpClient } from '@aurelia/fetch-client'
import './assets/css/styles.css'

Aurelia
  .register(
    RouterConfiguration.customize({ useUrlFragmentHash: true }), 
    Registration.singleton(IHttpClient, HttpClient),
    {
      register(container) {
        const http = container.get(IHttpClient);
        http.configure(config => {
          config.withBaseUrl('http://127.0.0.1:8020/api/v1/');
          config.withDefaults({
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          })
        })
      }
    }
  )
  .app(MyApp)
  .start()