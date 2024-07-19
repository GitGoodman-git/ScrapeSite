import pycountry
import pytz
def get_country_geolocation(country_code):
    try:
        country = pycountry.countries.get(alpha_2=country_code.upper())
        if country:return {'latitude': country.latitude, 'longitude': country.longitude}
    except:pass
    return False
def get_languages_for_country(country_code):
    try:
        country = pycountry.countries.get(alpha_2=country_code)
        if country:
            
         languages = []
         for language in pycountry.languages:
            if hasattr(language, 'alpha_2') and country.alpha_2 in language.scope:
                languages.append(language.name)

         return languages
 
    except Exception as e:pass
    return []
    
async def timezone(page,country_code):
    timezones = pytz.country_timezones.get(country_code, [])    
    if timezones:
     await page.evaluate(f"""
        Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {{
            value: function() {{
                return {{
                    timeZone: '{timezones[0]}'
                }};
            }}
        }});
    """)
async def geolocate(page, country_code):
        loc=get_country_geolocation(country_code)    
        await page.set_extra_http_headers({'Accept-Language':','.join(['en',*get_languages_for_country(country_code)])})
        await timezone(page,country_code)
        if loc:
            await page.evaluate('''(latitude, longitude) => {
            navigator.geolocation.getCurrentPosition = (success, error, options) => {
                const position = {
                    coords: {
                        latitude: latitude,
                        longitude: longitude,
                        accuracy: 100,
                    },
                };
                setTimeout(success.bind(null, position), 1000); // Simulate asynchronous behavior
            };
        }''', )
            return True 
        return False    