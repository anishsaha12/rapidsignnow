from django.db import models


class Address(models.Model):
    street_one = models.CharField(max_length=200)
    street_two = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=150, default="United States of America")
    gmaps_link = models.URLField(blank=True, null=True)

    #meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_coordinates(self):
        import requests
        address_string = self.street_one + ', ' 
        
        if self.street_two is not None:
            address_string += self.street_two + ', '
            
        address_string += self.city + ', ' + self.state + ', ' + self.zip_code + ', ' + self.country

        response_data = requests.get('https://maps.google.com/maps/api/geocode/json', {'address': address_string, 'key': 'AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'})
        try:
            latitude = response_data.json()['results'][0]['geometry']['location']['lat']
            longitude = response_data.json()['results'][0]['geometry']['location']['lng']
            return {'latitude': latitude, 'longitude': longitude}
        except:
            return None

    def get_driving_distance_from_address(self, destination_coordinates):
        import requests

        source_coordinates = self.get_coordinates()

        try:
            source_coordinates_string = source_coordinates['latitude'] + ',' + source_coordinates['longitude']
            destination_coordinates_string = destination_coordinates['latitude'] + ',' + destination_coordinates['longitude']
        except:
            return None

        response_data = requests.get('https://maps.googleapis.com/maps/api/distancematrix/json',
                                     {'origins': source_coordinates_string,
                                      'destinations': destination_coordinates_string, 'units': 'imperial'})

        try:
            distance_in_words = response_data.json()['rows'][0]['elements'][0]['distance']['text']
            return distance_in_words
        except:
            return None

    def simple_address(self):

        if self.street_two is None or self.street_two == "":
            address_string = self.street_one + ', ' + self.city + ', ' + self.state
        else:
            address_string = self.street_one + ', ' + self.street_two + ', ' + self.city + ', ' + self.state

        if self.zip_code is None or self.zip_code == "":
            address_string += ''
        else:
            address_string += ', ' + self.zip_code
        return address_string.encode('utf-8')

    def pdf_address(self):
        address_string = self.street_one + ', ' + self.street_two + ', ' + '<br />' + self.city + ', ' + '<br />' + \
                         self.state + ', ' + '<br />' + self.zip_code + ', ' + '<br />' + self.country
        return address_string.encode('utf-8')

    def re_render_gmaps_link(self):
        if self.gmaps_link is None:
            coordinates = self.get_coordinates()

            if coordinates is not None:
                self.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                       str(coordinates['longitude'])
                self.save()

        return ''

    def __str__(self):
        if self.street_two is None or self.street_two == "":
            address_string = self.street_one + ', ' + self.city + ', ' + self.state + ', '
                            # self.zip_code + ', ' + self.country
        else:
            address_string = self.street_one + ', ' + self.street_two + ', ' + self.city + ', ' + self.state + ', '
                            # self.zip_code + ', ' + self.country


        if self.zip_code is None or self.zip_code == "":
            address_string += self.country
        else:
            address_string += self.zip_code + ', ' + self.country


        # address_string = self.street_one + ', ' + self.street_two + ', ' + self.city + ', ' + self.state + ', ' + \
        #                  self.zip_code + ', ' + self.country
        return address_string.encode('utf-8')

    def __unicode__(self):
        if self.street_two is None or self.street_two == "":
            address_string = self.street_one + ', ' + self.city + ', ' + self.state + ', '
                            # self.zip_code + ', ' + self.country
        else:
            address_string = self.street_one + ', ' + self.street_two + ', ' + self.city + ', ' + self.state + ', '
                            # self.zip_code + ', ' + self.country


        if self.zip_code is None or self.zip_code == "":
            address_string += self.country
        else:
            address_string += self.zip_code + ', ' + self.country

        # address_string = self.street_one + ', ' + self.street_two + ', ' + self.city + ', ' + self.state + ', ' + \
        #                  self.zip_code + ', ' + self.country
        return address_string
