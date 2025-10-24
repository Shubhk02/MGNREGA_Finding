import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Search, MapPin, TrendingUp, Users, Briefcase } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const navigate = useNavigate();
  const [districts, setDistricts] = useState([]);
  const [filteredDistricts, setFilteredDistricts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [language, setLanguage] = useState('hi'); // 'hi' for Hindi, 'en' for English

  useEffect(() => {
    fetchDistricts();
  }, []);

  useEffect(() => {
    if (searchTerm === '') {
      setFilteredDistricts(districts);
    } else {
      const filtered = districts.filter((d) =>
        d.district_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        d.district_name_hi.includes(searchTerm)
      );
      setFilteredDistricts(filtered);
    }
  }, [searchTerm, districts]);

  const fetchDistricts = async () => {
    try {
      const response = await axios.get(`${API}/districts?state_code=UP`);
      if (response.data.success) {
        setDistricts(response.data.data);
        setFilteredDistricts(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching districts:', error);
      toast.error('Failed to load districts');
    } finally {
      setLoading(false);
    }
  };

  const handleDistrictSelect = (districtCode) => {
    navigate(`/district/${districtCode}`);
  };

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'hi' ? 'en' : 'hi');
  };

  const translations = {
    hi: {
      title: 'मनरेगा डैशबोर्ड',
      subtitle: 'उत्तर प्रदेश जिला प्रदर्शन ट्रैकर',
      search: 'खोजें... (जिला का नाम)',
      selectDistrict: 'जिला चुनें',
      loading: 'लोड हो रहा है...',
      stats: 'आंकड़े',
      districtCount: 'कुल जिले',
      language: 'English',
      about: 'मनरेगा के बारे में',
      aboutText: 'महात्मा गांधी राष्ट्रीय ग्रामीण रोजगार गारंटी अधिनियम (मनरेगा) भारत में ग्रामीण परिवारों को एक वित्तीय वर्ष में कम से कम 100 दिनों की मजदूरी रोजगार की कानूनी गारंटी प्रदान करता है।'
    },
    en: {
      title: 'MGNREGA Dashboard',
      subtitle: 'Uttar Pradesh District Performance Tracker',
      search: 'Search... (District Name)',
      selectDistrict: 'Select a District',
      loading: 'Loading...',
      stats: 'Statistics',
      districtCount: 'Total Districts',
      language: 'हिंदी',
      about: 'About MGNREGA',
      aboutText: 'Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA) provides a legal guarantee of 100 days of wage employment in a financial year to rural households in India.'
    }
  };

  const t = translations[language];

  return (
    <div className="min-h-screen" data-testid="home-page">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 via-white to-green-500 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-center md:text-left">
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-800 mb-2" data-testid="page-title">
                {t.title}
              </h1>
              <p className="text-base sm:text-lg text-gray-600">{t.subtitle}</p>
            </div>
            <Button
              onClick={toggleLanguage}
              variant="outline"
              className="bg-white hover:bg-gray-50 border-2 border-gray-300"
              data-testid="language-toggle-btn"
            >
              <MapPin className="w-4 h-4 mr-2" />
              {t.language}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* About Section */}
        <Card className="mb-8 bg-white/90 backdrop-blur-sm shadow-xl border-0">
          <CardHeader>
            <CardTitle className="text-2xl flex items-center gap-2 text-blue-900">
              <Briefcase className="w-6 h-6" />
              {t.about}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 leading-relaxed">{t.aboutText}</p>
          </CardContent>
        </Card>

        {/* Search Section */}
        <Card className="mb-8 bg-white/90 backdrop-blur-sm shadow-xl border-0">
          <CardHeader>
            <CardTitle className="text-xl text-gray-800">{t.selectDistrict}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative" data-testid="district-search-container">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder={t.search}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 py-6 text-lg border-2 focus:border-blue-500 rounded-xl"
                data-testid="district-search-input"
              />
            </div>
          </CardContent>
        </Card>

        {/* Stats */}
        {!loading && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
            <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 shadow-xl hover:shadow-2xl transition-all duration-300">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100 text-sm mb-1">{t.districtCount}</p>
                    <p className="text-4xl font-bold" data-testid="total-districts-count">{districts.length}</p>
                  </div>
                  <MapPin className="w-12 h-12 text-blue-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white border-0 shadow-xl hover:shadow-2xl transition-all duration-300">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100 text-sm mb-1">Active Workers</p>
                    <p className="text-4xl font-bold">2.5L+</p>
                  </div>
                  <Users className="w-12 h-12 text-green-200" />
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white border-0 shadow-xl hover:shadow-2xl transition-all duration-300">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-orange-100 text-sm mb-1">Works Ongoing</p>
                    <p className="text-4xl font-bold">5000+</p>
                  </div>
                  <TrendingUp className="w-12 h-12 text-orange-200" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Districts Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            Array(6).fill(0).map((_, i) => (
              <Card key={i} className="bg-white shadow-lg border-0">
                <CardContent className="p-6">
                  <Skeleton height={30} className="mb-2" />
                  <Skeleton height={20} width={150} />
                </CardContent>
              </Card>
            ))
          ) : filteredDistricts.length > 0 ? (
            filteredDistricts.map((district) => (
              <Card
                key={district.district_code}
                className="bg-white hover:bg-gradient-to-br hover:from-blue-50 hover:to-white shadow-lg hover:shadow-2xl border-2 border-transparent hover:border-blue-300 cursor-pointer group transition-all duration-300"
                onClick={() => handleDistrictSelect(district.district_code)}
                data-testid={`district-card-${district.district_code}`}
              >
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-800 mb-2 group-hover:text-blue-600 transition-colors">
                        {language === 'hi' ? district.district_name_hi : district.district_name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {language === 'hi' ? district.district_name : district.district_name_hi}
                      </p>
                      <div className="mt-4 flex items-center text-sm text-gray-600">
                        <MapPin className="w-4 h-4 mr-1" />
                        <span>{district.state_name_hi}</span>
                      </div>
                    </div>
                    <div className="text-blue-500 group-hover:text-blue-700 transition-transform group-hover:translate-x-1">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="col-span-full text-center py-12">
              <p className="text-gray-500 text-lg">No districts found</p>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-16 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-sm">
            © 2025 MGNREGA Dashboard | Ministry of Rural Development, Government of India
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Home;