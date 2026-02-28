/* src/pages/client/storico/storico.js */
import { resolve } from '@aurelia/kernel'
import { ApiService } from '@/services/api-service'
import { createIcons, icons } from 'lucide'

export default class Storico {
  api = resolve(ApiService)
  prenotazioni = []

  async attaching() {

    this.prenotazioni = await this.api.getMiePrenotazioni()
    lucide.createIcons()
  }

  getStatusClass(stato) {
    const mapping = {
      'CONF': 'confirmed',
      'PEND': 'pending',
      'CANC': 'cancelled'
    }
    return mapping[stato] || 'pending'
  }
}

/**
 * Value Converter to format date into template 
 * Use: ${p.data | dateFormat}
 */
export class DateFormatValueConverter {

  toView(value) {

    if (!value) {

      return ''
    }

    const date = new Date(value)
    return date.toLocaleDateString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  }
}