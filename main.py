import dash
import geopandas as gpd
import plotly.express as px
import pandas as pd
from dash import Dash, html, dcc, dash_table, Input, Output, State
from fuzzywuzzy import process
from datetime import date

# Included the columns before reading the CSV file to reduce loading time
columns_to_include = ['Start', 'End', 'Duration(Days)', 'Main Cause', 'State', 'Districts']
df = pd.read_csv('src/IndiaFloodInventory.csv', usecols=columns_to_include)
df = df.rename(columns={
    'Start': 'Start Date',
    'End': 'End Date',
    'Duration(Days)': 'Duration (in days)',
    'Cause': 'Main Cause',
    'State': 'Affected State',
    'Districts': 'Affected District',
})

# Convert dates to datetime and then format them to DD/MM/YYYY
df['Start Date'] = pd.to_datetime(df['Start Date'], format='%d/%m/%Y').dt.strftime('%d/%m/%Y')
df['End Date'] = pd.to_datetime(df['End Date'], format='%d/%m/%Y').dt.strftime('%d/%m/%Y')

# State-district list of India
districts_of_states = {
    'Andaman and Nicobar Islands': [
        'Nicobars', 'North and Middle Andaman', 'South Andaman'
    ],
    'Andhra Pradesh': [
        'Anantapur', 'Chittoor', 'East Godavari', 'Guntur', 'Kadapa',
        'Krishna', 'Kurnool', 'Prakasam', 'Sri Potti Sriramulu Nellore',
        'Srikakulam', 'Visakhapatnam', 'Vizianagaram', 'West Godavari'
    ],
    'Arunachal Pradesh': [
        'Anjaw', 'Changlang', 'Dibang Valley', 'East Kameng', 'East Siang',
        'Kamle', 'Kra Daadi', 'Kurung Kumey', 'Lepa Rada', 'Lohit', 'Longding',
        'Lower Dibang Valley', 'Lower Siang', 'Lower Subansiri', 'Namsai',
        'Pakke Kessang', 'Papum Pare', 'Shi Yomi', 'Siang', 'Tawang', 'Tirap',
        'Upper Siang', 'Upper Subansiri', 'West Kameng', 'West Siang'
    ],
    'Assam': [
        'Baksa', 'Barpeta', 'Biswanath', 'Bongaigaon', 'Cachar', 'Charaideo',
        'Chirang', 'Darrang', 'Dhemaji', 'Dhubri', 'Dibrugarh', 'Dima Hasao',
        'Goalpara', 'Golaghat', 'Hailakandi', 'Hojai', 'Jorhat', 'Kamrup',
        'Kamrup Metropolitan', 'Karbi Anglong', 'Karimganj', 'Kokrajhar',
        'Lakhimpur', 'Majuli', 'Morigaon', 'Nagaon', 'Nalbari', 'Sivasagar',
        'Sonitpur', 'South Salmara-Mankachar', 'Tinsukia', 'Udalguri', 'West Karbi Anglong'
    ],
    'Bihar': [
        'Araria', 'Arwal', 'Aurangabad', 'Banka', 'Begusarai', 'Bhagalpur',
        'Bhojpur', 'Buxar', 'Darbhanga', 'East Champaran', 'Gaya', 'Gopalganj',
        'Jamui', 'Jehanabad', 'Kaimur', 'Katihar', 'Khagaria', 'Kishanganj',
        'Lakhisarai', 'Madhepura', 'Madhubani', 'Munger', 'Muzaffarpur', 'Nalanda',
        'Nawada', 'Patna', 'Purnia', 'Rohtas', 'Saharsa', 'Samastipur', 'Saran',
        'Sheikhpura', 'Sheohar', 'Sitamarhi', 'Siwan', 'Supaul', 'Vaishali', 'West Champaran'
    ],
    'Chandigarh': [
        'Chandigarh'
    ],
    'Chhattisgarh': [
        'Balod', 'Baloda Bazar', 'Balrampur', 'Bastar', 'Bemetara', 'Bijapur',
        'Bilaspur', 'Dantewada', 'Dhamtari', 'Durg', 'Gariaband', 'Janjgir-Champa',
        'Jashpur', 'Kanker', 'Kawardha', 'Kondagaon', 'Korba', 'Koriya', 'Mahasamund',
        'Mungeli', 'Narayanpur', 'Raigarh', 'Raipur', 'Rajnandgaon', 'Sukma', 'Surajpur',
        'Surguja'
    ],
    'Dadra and Nagar Haveli and Daman and Diu': [
        'Dadra and Nagar Haveli', 'Daman', 'Diu'
    ],
    'Delhi': [
        'Central Delhi', 'East Delhi', 'New Delhi', 'North Delhi', 'North East Delhi',
        'North West Delhi', 'Shahdara', 'South Delhi', 'South East Delhi', 'South West Delhi',
        'West Delhi'
    ],
    'Goa': [
        'North Goa', 'South Goa'
    ],
    'Gujarat': [
        'Ahmedabad', 'Amreli', 'Anand', 'Aravalli', 'Banaskantha', 'Bharuch', 'Bhavnagar',
        'Botad', 'Chhota Udaipur', 'Dahod', 'Dang', 'Devbhoomi Dwarka', 'Gandhinagar',
        'Gir Somnath', 'Jamnagar', 'Junagadh', 'Kutch', 'Kheda', 'Mahisagar', 'Mehsana',
        'Morbi', 'Narmada', 'Navsari', 'Panchmahal', 'Patan', 'Porbandar', 'Rajkot', 'Sabarkantha',
        'Surat', 'Surendranagar', 'Tapi', 'Vadodara', 'Valsad'
    ],
    'Haryana': [
        'Ambala', 'Bhiwani', 'Charkhi Dadri', 'Faridabad', 'Fatehabad', 'Gurugram',
        'Hisar', 'Jhajjar', 'Jind', 'Kaithal', 'Karnal', 'Kurukshetra', 'Mahendragarh',
        'Nuh', 'Palwal', 'Panchkula', 'Panipat', 'Rewari', 'Rohtak', 'Sirsa', 'Sonipat',
        'Yamunanagar'
    ],
    'Himachal Pradesh': [
        'Bilaspur', 'Chamba', 'Hamirpur', 'Kangra', 'Kinnaur', 'Kullu', 'Lahaul and Spiti',
        'Mandi', 'Shimla', 'Sirmaur', 'Solan', 'Una'
    ],
    'Jammu and Kashmir': [
        'Anantnag', 'Bandipora', 'Baramulla', 'Budgam', 'Doda', 'Ganderbal', 'Jammu',
        'Kathua', 'Kishtwar', 'Kulgam', 'Kupwara', 'Poonch', 'Pulwama', 'Rajouri',
        'Ramban', 'Reasi', 'Samba', 'Shopian', 'Srinagar', 'Udhampur'
    ],
    'Jharkhand': [
        'Bokaro', 'Chatra', 'Deoghar', 'Dhanbad', 'Dumka', 'East Singhbhum', 'Garhwa',
        'Giridih', 'Godda', 'Gumla', 'Hazaribagh', 'Jamtara', 'Khunti', 'Koderma',
        'Latehar', 'Lohardaga', 'Pakur', 'Palamu', 'Ramgarh', 'Ranchi', 'Sahibganj',
        'Seraikela Kharsawan', 'Simdega', 'West Singhbhum'
    ],
    'Karnataka': [
        'Bagalkot', 'Ballari', 'Belagavi', 'Bengaluru Rural', 'Bengaluru Urban',
        'Bidar', 'Chamarajanagar', 'Chikkaballapur', 'Chikkamagaluru', 'Chitradurga',
        'Dakshina Kannada', 'Davanagere', 'Dharwad', 'Gadag', 'Hassan', 'Haveri',
        'Kalaburagi', 'Kodagu', 'Kolar', 'Koppal', 'Mandya', 'Mysuru', 'Raichur',
        'Ramanagara', 'Shivamogga', 'Tumakuru', 'Udupi', 'Uttara Kannada', 'Vijayapura',
        'Yadgir'
    ],
    'Kerala': [
        'Alappuzha', 'Ernakulam', 'Idukki', 'Kannur', 'Kasaragod', 'Kollam', 'Kottayam',
        'Kozhikode', 'Malappuram', 'Palakkad', 'Pathanamthitta', 'Thiruvananthapuram',
        'Thrissur', 'Wayanad'
    ],
    'Ladakh': [
        'Kargil', 'Leh'
    ],
    'Lakshadweep': [
        'Agatti', 'Amini', 'Andrott', 'Bitra', 'Chetlat', 'Kadmat', 'Kalpeni', 'Kavaratti',
        'Kiltan', 'Minicoy'
    ],
    'Madhya Pradesh': [
        'Agar Malwa', 'Alirajpur', 'Anuppur', 'Ashoknagar', 'Balaghat', 'Barwani',
        'Betul', 'Bhind', 'Bhopal', 'Burhanpur', 'Chhatarpur', 'Chhindwara', 'Damoh',
        'Datia', 'Dewas', 'Dhar', 'Dindori', 'Guna', 'Gwalior', 'Harda', 'Hoshangabad',
        'Indore', 'Jabalpur', 'Jhabua', 'Katni', 'Khandwa', 'Khargone', 'Mandla', 'Mandsaur',
        'Morena', 'Narsinghpur', 'Neemuch', 'Panna', 'Raisen', 'Rajgarh', 'Ratlam',
        'Rewa', 'Sagar', 'Satna', 'Sehore', 'Seoni', 'Shahdol', 'Shajapur', 'Sheopur',
        'Shivpuri', 'Sidhi', 'Singrauli', 'Tikamgarh', 'Ujjain', 'Umaria', 'Vidisha'
    ],
    'Maharashtra': [
        'Ahmednagar', 'Akola', 'Amravati', 'Aurangabad', 'Beed', 'Bhandara', 'Buldhana',
        'Chandrapur', 'Dhule', 'Gadchiroli', 'Gondia', 'Hingoli', 'Jalgaon', 'Jalna',
        'Kolhapur', 'Latur', 'Mumbai City', 'Mumbai Suburban', 'Nagpur', 'Nanded',
        'Nandurbar', 'Nashik', 'Osmanabad', 'Palghar', 'Parbhani', 'Pune', 'Raigad',
        'Ratnagiri', 'Sangli', 'Satara', 'Sindhudurg', 'Solapur', 'Thane', 'Wardha',
        'Washim', 'Yavatmal'
    ],
    'Manipur': [
        'Bishnupur', 'Chandel', 'Churachandpur', 'Imphal East', 'Imphal West',
        'Jiribam', 'Kakching', 'Kamjong', 'Kangpokpi', 'Noney', 'Pherzawl', 'Senapati',
        'Tamenglong', 'Tengnoupal', 'Thoubal', 'Ukhrul'
    ],
    'Meghalaya': [
        'East Garo Hills', 'East Jaintia Hills', 'East Khasi Hills', 'North Garo Hills',
        'Ri Bhoi', 'South Garo Hills', 'South West Garo Hills', 'South West Khasi Hills',
        'West Garo Hills', 'West Jaintia Hills', 'West Khasi Hills'
    ],
    'Mizoram': [
        'Aizawl', 'Champhai', 'Hnahthial', 'Khawzawl', 'Kolasib', 'Lawngtlai', 'Lunglei', 'Mamit', 'Saiha', 'Saitual', 'Serchhip'
    ],
    'Nagaland': [
        'Dimapur', 'Kiphire', 'Kohima', 'Longleng', 'Mokokchung', 'Mon', 'Peren',
        'Phek', 'Tuensang', 'Wokha', 'Zunheboto'
    ],
    'Odisha': [
        'Angul', 'Balangir', 'Balasore', 'Bargarh', 'Bhadrak', 'Boudh', 'Cuttack',
        'Deogarh', 'Dhenkanal', 'Gajapati', 'Ganjam', 'Jagatsinghpur', 'Jajpur',
        'Jharsuguda', 'Kalahandi', 'Kandhamal', 'Kendrapara', 'Kendujhar', 'Khordha',
        'Koraput', 'Malkangiri', 'Mayurbhanj', 'Nabarangpur', 'Nayagarh', 'Nuapada',
        'Puri', 'Rayagada', 'Sambalpur', 'Subarnapur', 'Sundargarh'
    ],
    'Puducherry': [
        'Karaikal', 'Mahe', 'Puducherry', 'Yanam'
    ],
    'Punjab': [
        'Amritsar', 'Barnala', 'Bathinda', 'Faridkot', 'Fatehgarh Sahib', 'Fazilka',
        'Ferozepur', 'Gurdaspur', 'Hoshiarpur', 'Jalandhar', 'Kapurthala', 'Ludhiana',
        'Mansa', 'Moga', 'Pathankot', 'Patiala', 'Rupnagar', 'Sahibzada Ajit Singh Nagar',
        'Sangrur', 'Shahid Bhagat Singh Nagar', 'Sri Muktsar Sahib', 'Tarn Taran'
    ],
    'Rajasthan': [
        'Ajmer', 'Alwar', 'Banswara', 'Baran', 'Barmer', 'Bharatpur', 'Bhilwara',
        'Bikaner', 'Bundi', 'Chittorgarh', 'Churu', 'Dausa', 'Dholpur', 'Dungarpur',
        'Hanumangarh', 'Jaipur', 'Jaisalmer', 'Jalore', 'Jhalawar', 'Jhunjhunu',
        'Jodhpur', 'Karauli', 'Kota', 'Nagaur', 'Pali', 'Pratapgarh', 'Rajsamand',
        'Sawai Madhopur', 'Sikar', 'Sirohi', 'Sri Ganganagar', 'Tonk', 'Udaipur'
    ],
    'Sikkim': [
        'East Sikkim', 'North Sikkim', 'South Sikkim', 'West Sikkim'
    ],
    'Tamil Nadu': [
        'Ariyalur', 'Chengalpattu', 'Chennai', 'Coimbatore', 'Cuddalore', 'Dharmapuri',
        'Dindigul', 'Erode', 'Kallakurichi', 'Kanchipuram', 'Kanyakumari', 'Karur',
        'Krishnagiri', 'Madurai', 'Mayiladuthurai', 'Nagapattinam', 'Namakkal', 'Nilgiris',
        'Perambalur', 'Pudukkottai', 'Ramanathapuram', 'Ranipet', 'Salem', 'Sivaganga',
        'Tenkasi', 'Thanjavur', 'Theni', 'Thoothukudi', 'Tiruchirappalli', 'Tirunelveli',
        'Tirupathur', 'Tiruppur', 'Tiruvallur', 'Tiruvannamalai', 'Tiruvarur', 'Vellore',
        'Viluppuram', 'Virudhunagar'
    ],
    'Telangana': [
        'Adilabad', 'Bhadradri Kothagudem', 'Hyderabad', 'Jagtial', 'Jangaon',
        'Jayashankar Bhupalpally', 'Jogulamba Gadwal', 'Kamareddy', 'Karimnagar', 'Khammam',
        'Kumuram Bheem', 'Mahabubabad', 'Mahabubnagar', 'Mancherial', 'Medak', 'Medchal–Malkajgiri',
        'Mulugu', 'Nagarkurnool', 'Nalgonda', 'Narayanpet', 'Nirmal', 'Nizamabad', 'Peddapalli',
        'Rajanna Sircilla', 'Ranga Reddy', 'Sangareddy', 'Siddipet', 'Suryapet', 'Vikarabad',
        'Wanaparthy', 'Warangal Rural', 'Warangal Urban', 'Yadadri Bhuvanagiri'
    ],
    'Tripura': [
        'Dhalai', 'Gomati', 'Khowai', 'North Tripura', 'Sepahijala', 'South Tripura',
        'Unakoti', 'West Tripura'
    ],
    'Uttar Pradesh': [
        'Agra', 'Aligarh', 'Ambedkar Nagar', 'Amethi', 'Amroha', 'Auraiya', 'Ayodhya',
        'Azamgarh', 'Baghpat', 'Bahraich', 'Ballia', 'Balrampur', 'Banda', 'Barabanki',
        'Bareilly', 'Basti', 'Bhadohi', 'Bijnor', 'Budaun', 'Bulandshahr', 'Chandauli',
        'Chitrakoot', 'Deoria', 'Etah', 'Etawah', 'Farrukhabad', 'Fatehpur', 'Firozabad',
        'Gautam Buddh Nagar', 'Ghaziabad', 'Ghazipur', 'Gonda', 'Gorakhpur', 'Hamirpur',
        'Hapur', 'Hardoi', 'Hathras', 'Jalaun', 'Jaunpur', 'Jhansi', 'Kannauj', 'Kanpur Dehat',
        'Kanpur Nagar', 'Kasganj', 'Kaushambi', 'Kheri', 'Kushinagar', 'Lalitpur', 'Lucknow',
        'Maharajganj', 'Mahoba', 'Mainpuri', 'Mathura', 'Mau', 'Meerut', 'Mirzapur', 'Moradabad',
        'Muzaffarnagar', 'Pilibhit', 'Pratapgarh', 'Prayagraj', 'Rae Bareli', 'Rampur', 'Saharanpur',
        'Sambhal', 'Sant Kabir Nagar', 'Shahjahanpur', 'Shamli', 'Shravasti', 'Siddharthnagar', 'Sitapur',
        'Sonbhadra', 'Sultanpur', 'Unnao', 'Varanasi'
    ],
    'Uttarakhand': [
        'Almora', 'Bageshwar', 'Chamoli', 'Champawat', 'Dehradun', 'Haridwar', 'Nainital',
        'Pauri Garhwal', 'Pithoragarh', 'Rudraprayag', 'Tehri Garhwal', 'Udham Singh Nagar',
        'Uttarkashi'
    ],
    'West Bengal': [
        'Alipurduar', 'Bankura', 'Birbhum', 'Cooch Behar', 'Dakshin Dinajpur', 'Darjeeling',
        'Hooghly', 'Howrah', 'Jalpaiguri', 'Jhargram', 'Kalimpong', 'Kolkata', 'Malda',
        'Murshidabad', 'Nadia', 'North 24 Parganas', 'Paschim Bardhaman', 'Paschim Medinipur',
        'Purba Bardhaman', 'Purba Medinipur', 'Purulia', 'South 24 Parganas', 'Uttar Dinajpur'
    ]
}


districts_shapefile_path = "src/India_Districts.shp"
states_shapefile_path = "src/india_states.shp"
districts_gdf = gpd.read_file(districts_shapefile_path)
states_gdf = gpd.read_file(states_shapefile_path)

external_stylesheets = ['assets/custom.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

def create_default_map():
    fig = px.choropleth_mapbox(
        states_gdf,
        geojson=states_gdf.geometry.__geo_interface__,
        locations=states_gdf.index,
        color_discrete_map={},
        mapbox_style="carto-positron",
        center={"lat": 22.5937, "lon": 78.9629},
        zoom=3.3,
        opacity=0.6
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

default_map_fig = create_default_map()

navbar = html.Div(
    html.Div("FLOOD DATA VISUALISER", className="navbar-brand"),
    className="navbar"
)

# Table creator
def create_data_table(dataframe):
    return dash_table.DataTable(
        id='datatable-interactivity',
        data=dataframe.to_dict('records'), 
        columns=[{"name": i, "id": i, "selectable": True} for i in dataframe.columns],
        row_selectable="single",
        selected_rows=[],
        page_size=50,
        fixed_rows={'headers': True},
        style_table={'height': '500px', 'overflowY': 'auto'},
        style_header={
            'backgroundColor': 'rgb(173, 216, 230)',
            'color': 'black',
            'borderRadius': '4px',
            'textAlign': 'center',
            'fontWeight': 'bold',
            'fontSize': '12px',
            'fontFamily': 'System-UI',
            'whiteSpace': 'normal',
            'height': 'auto',
            'className': 'data-table-header'
        },
        style_data={
            'color': 'black',
            'backgroundColor': 'white',
            'fontSize': '12px',
            'fontFamily': 'System-UI'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(220, 220, 220)',
                'fontSize': '12px',
                'fontFamily': 'System-UI'
            }
        ],
        style_cell={
            'textAlign': 'left',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': 0,
        },
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in dataframe.to_dict('records')
        ],
        tooltip_delay=5,
        tooltip_duration=None,
        style_cell_conditional=[
            {'if': {'column_id': 'Start Date'},
             'width': '10%'},
            {'if': {'column_id': 'End Date'},
             'width': '10%'},
            {'if': {'column_id': 'Duration (in days)'},
             'width': '7%'},
            {'if': {'column_id': 'Main Cause'},
             'width': '15%'},
        ]
    )

app.layout = html.Div([
    navbar,
    html.Div([
        html.Div([
            html.P("Flood Data", className='box-header'),
            html.Div([
                html.Div([
                    html.Div("Apply Filter:", id='filter-header'),
                    html.Div([
                        html.Div([
                            html.Label('Start Date:'),
                            dcc.DatePickerSingle(
                                id='start-date',
                                month_format='MMMM YYYY',
                                placeholder='DD/MM/YYYY',
                                display_format='DD/MM/YYYY',
                                date=date(2020, 2, 29),
                                max_date_allowed=date(2023, 9, 10), #y/m/d
                                className="form-control datepicker-single"),
                                html.P("max : 10/09/2023", className='infos'),       
                        ], className="form-group"),
                        html.Div([
                            html.Label('End Date:'),
                            dcc.DatePickerSingle(
                                id='end-date',
                                month_format='MMMM YYYY',
                                placeholder='DD/MM/YYYY',
                                display_format='DD/MM/YYYY',
                                date=date(2020, 2, 29),
                                min_date_allowed=date(1967, 7, 8), #ymd
                                className="form-control datepicker-single"),
                                html.P("min : 08/07/1967", className='infos'),
                        ], className="form-group"),
                        html.Div([
                            html.Label('State:'),
                            dcc.Dropdown(
                                id='state',
                                options=[{'label': state, 'value': state} for state in districts_of_states.keys()],
                                placeholder='SELECT STATE',
                                className="form-control dropdown",
                            )], className="form-group"),
                        html.Div([
                            html.Label('District:'),
                            dcc.Dropdown(
                                id='district', 
                                placeholder='SELECT DISTRICT',
                                className="form-control dropdown",
                                )], className="form-group"),
                    ], className="form-inline"),
                    html.Div([
                        html.Button('Submit', id='submit-button', n_clicks=0, className="filter-button"),
                        html.Button('Reset Filters', id='reset-button', n_clicks=0, className="filter-button"),
                        html.Button('Delete All Filters', id='reset-all-button', n_clicks=0, className="filter-button"),
                    ], className="form-buttons"),
                ], className='filter-box'),
                html.Div(id='datatable-container', className='datatable-container', children=create_data_table(df)),
            ], className='horizontal-flex'),
        ], className='table-box'),
        html.Div([
            html.Div([
                dcc.RadioItems(
                    id='highlight-option',
                    options=[
                        {'label': 'Show States', 'value': 'state'},
                        {'label': 'Show Districts', 'value': 'district'}
                    ],
                    value='state',
                    labelStyle={'display': 'inline-block'}
                )], className='radio-buttons'),
            html.Div(className="map-container"),
            dcc.Graph(id='map-graph', figure=default_map_fig)
        ], className='map-box'),
    ], className='container')
], className='content')

@app.callback(
    Output('datatable-container', 'children'),
    Output('start-date', 'date'),
    Output('end-date', 'date'),
    Output('state', 'value'),
    Output('district', 'value'),
    Input('submit-button', 'n_clicks'),
    Input('reset-button', 'n_clicks'),
    Input('reset-all-button', 'n_clicks'),
    State('start-date', 'date'),
    State('end-date', 'date'),
    State('state', 'value'),
    State('district', 'value')
)
def update_data_table(submit_n_clicks, reset_n_clicks, reset_all_n_clicks, start_date, end_date, selected_state, selected_district):
    ctx = dash.callback_context
    if not ctx.triggered:
        return create_data_table(df), None, None, None, None

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'reset-all-button' or button_id == 'reset-button':
        return create_data_table(df), None, None, None, None

    filtered_df = df.copy()
    if button_id == 'submit-button':
        if start_date:
            start_date = pd.to_datetime(start_date, format='%Y-%m-%d').strftime('%d/%m/%Y')
            filtered_df = filtered_df[filtered_df['Start Date'] >= start_date]
        if end_date:
            end_date = pd.to_datetime(end_date, format='%Y-%m-%d').strftime('%d/%m/%Y')
            filtered_df = filtered_df[filtered_df['End Date'] <= end_date]
        if selected_state:
            filtered_df = filtered_df[filtered_df['Affected State'].str.contains(selected_state, na=False)]
        if selected_district:
            filtered_df = filtered_df[filtered_df['Affected District'].str.contains(selected_district, na=False)]

    return create_data_table(filtered_df), start_date, end_date, selected_state, selected_district

@app.callback(
    Output('district', 'options'),
    Input('state', 'value')
)
def set_district_options(selected_state):
    if selected_state is None:
        return []
    return [{'label': district, 'value': district} for district in districts_of_states[selected_state]]

@app.callback(
    Output('map-graph', 'figure'),
    Input('datatable-interactivity', 'derived_virtual_selected_rows'),
    Input('highlight-option', 'value'),
    State('datatable-interactivity', 'data')
)
def update_datatable_interactivity(selected_rows, highlight_option, table_data):
    if highlight_option == 'state':
        default_gdf = states_gdf
        hover_name_col = 'ST_NM'
    else:
        default_gdf = districts_gdf
        hover_name_col = 'Dist_Name'

    if selected_rows is None or len(selected_rows) == 0:
        fig = px.choropleth_mapbox(
            default_gdf,
            geojson=default_gdf.geometry.__geo_interface__,
            locations=default_gdf.index,
            hover_name=hover_name_col,
            color_continuous_scale=['lightgrey', 'red'],
            mapbox_style="carto-positron",
            center={"lat": 22.5937, "lon": 78.9629},
            zoom=3.3,
            opacity=0.6
        )
    else:
        selected_data = [table_data[i] for i in selected_rows]
        selected_row = selected_data[0]

        affected_states = selected_row['Affected State'].split(', ') if isinstance(selected_row['Affected State'], str) else []
        affected_districts = selected_row['Affected District'].split(', ') if isinstance(selected_row['Affected District'], str) else []

        matched_states = [process.extractOne(state, states_gdf['ST_NM'].unique())[0] for state in affected_states]
        matched_states_gdf = states_gdf[states_gdf['ST_NM'].isin(matched_states)]

        matched_districts = [process.extractOne(district, districts_gdf['Dist_Name'].unique())[0] for district in affected_districts]
        matched_districts_gdf = districts_gdf[districts_gdf['Dist_Name'].isin(matched_districts)]

        if highlight_option == 'state':
            geojson_data = matched_states_gdf.geometry.__geo_interface__
            locations = matched_states_gdf.index
            hover_name = 'ST_NM'
        else:
            geojson_data = matched_districts_gdf.geometry.__geo_interface__
            locations = matched_districts_gdf.index
            hover_name = 'Dist_Name'

        fig = px.choropleth_mapbox(
            matched_states_gdf if highlight_option == 'state' else matched_districts_gdf,
            geojson=geojson_data,
            locations=locations,
            hover_name=hover_name, 
            color_continuous_scale=['lightgrey', 'red'],
            mapbox_style="carto-positron",
            center={"lat": 22.5937, "lon": 78.9629},
            zoom=3.3,
            opacity=0.6
        )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
