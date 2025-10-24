import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  ArrowLeft,
  Users,
  Briefcase,
  IndianRupee,
  TrendingUp,
  TrendingDown,
  Calendar,
  Building2
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Skeleton from 'react-loading-skeleton';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DistrictDetail = () => {
  const { districtCode } = useParams();
  const navigate = useNavigate();
  const [currentData, setCurrentData] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [language, setLanguage] = useState('hi');

  useEffect(() => {
    fetchAllData();
  }, [districtCode]);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [currentRes, historyRes, compareRes] = await Promise.all([
        axios.get(`${API}/district/${districtCode}/current`),
        axios.get(`${API}/district/${districtCode}/history?months=6`),
        axios.get(`${API}/district/${districtCode}/compare`)
      ]);

      if (currentRes.data.success) setCurrentData(currentRes.data.data);
      if (historyRes.data.success) setHistoricalData(historyRes.data.data);
      if (compareRes.data.success) setComparison(compareRes.data.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load district data');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 10000000) return `₹${(num / 10000000).toFixed(2)}Cr`;
    if (num >= 100000) return `₹${(num / 100000).toFixed(2)}L`;
    if (num >= 1000) return `₹${(num / 1000).toFixed(2)}K`;
    return num?.toLocaleString('en-IN') || '0';
  };

  const formatPercentage = (val) => {
    const sign = val >= 0 ? '+' : '';
    return `${sign}${val?.toFixed(1)}%`;
  };

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'hi' ? 'en' : 'hi');
  };

  const translations = {
    hi: {
      back: 'वापस जाएं',
      currentPerformance: 'वर्तमान प्रदर्शन',
      totalWorkers: 'कुल कर्मचारी',
      workCompleted: 'कार्य पूर्ण',
      workOngoing: 'चल रहे कार्य',
      avgWage: 'औसत मजदूरी',
      budgetAllocated: 'आवंटित बजट',
      budgetSpent: 'खर्च किया गया बजट',
      personDays: 'व्यक्ति दिवस',
      comparison: 'पिछले महीने की तुलना',
      historicalTrend: 'ऐतिहासिक प्रवृत्ति (6 महीने)',
      month: 'महीना',
      language: 'English'
    },
    en: {
      back: 'Back to Districts',
      currentPerformance: 'Current Performance',
      totalWorkers: 'Total Workers',
      workCompleted: 'Work Completed',
      workOngoing: 'Ongoing Works',
      avgWage: 'Average Wage',
      budgetAllocated: 'Budget Allocated',
      budgetSpent: 'Budget Spent',
      personDays: 'Person Days',
      comparison: 'Comparison with Last Month',
      historicalTrend: 'Historical Trend (6 Months)',
      month: 'Month',
      language: 'हिंदी'
    }
  };

  const t = translations[language];

  const MetricCard = ({ title, value, icon: Icon, trend, color }) => (
    <Card className={`bg-gradient-to-br ${color} text-white border-0 shadow-xl hover:shadow-2xl transition-all duration-300`}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm opacity-90 mb-2">{title}</p>
            <p className="text-3xl font-bold mb-2" data-testid={`metric-${title.toLowerCase().replace(/\s+/g, '-')}`}>
              {value}
            </p>
            {trend !== undefined && (
              <div className="flex items-center gap-1 text-sm">
                {trend >= 0 ? (
                  <TrendingUp className="w-4 h-4" />
                ) : (
                  <TrendingDown className="w-4 h-4" />
                )}
                <span>{formatPercentage(trend)}</span>
              </div>
            )}
          </div>
          <Icon className="w-12 h-12 opacity-80" />
        </div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 p-8">
        <div className="max-w-7xl mx-auto">
          <Skeleton height={60} className="mb-8" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {Array(4).fill(0).map((_, i) => (
              <Skeleton key={i} height={150} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50" data-testid="district-detail-page">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 via-white to-green-500 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <Button
                onClick={() => navigate('/')}
                variant="outline"
                className="mb-4 bg-white hover:bg-gray-50"
                data-testid="back-to-districts-btn"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                {t.back}
              </Button>
              <h1 className="text-3xl sm:text-4xl font-bold text-gray-800" data-testid="district-title">
                {districtCode} - Performance Dashboard
              </h1>
            </div>
            <Button
              onClick={toggleLanguage}
              variant="outline"
              className="bg-white hover:bg-gray-50"
              data-testid="language-toggle-detail-btn"
            >
              {t.language}
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Current Performance Metrics */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <Calendar className="w-6 h-6" />
            {t.currentPerformance}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title={t.totalWorkers}
              value={currentData?.total_workers?.toLocaleString('en-IN') || '0'}
              icon={Users}
              trend={comparison?.changes?.total_workers}
              color="from-blue-500 to-blue-600"
            />
            <MetricCard
              title={t.workCompleted}
              value={currentData?.work_completed || '0'}
              icon={Briefcase}
              trend={comparison?.changes?.work_completed}
              color="from-green-500 to-green-600"
            />
            <MetricCard
              title={t.avgWage}
              value={`₹${currentData?.average_wage || '0'}`}
              icon={IndianRupee}
              color="from-purple-500 to-purple-600"
            />
            <MetricCard
              title={t.personDays}
              value={currentData?.person_days_generated?.toLocaleString('en-IN') || '0'}
              icon={Building2}
              trend={comparison?.changes?.person_days_generated}
              color="from-orange-500 to-orange-600"
            />
          </div>
        </div>

        {/* Budget Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card className="bg-white shadow-xl border-0">
            <CardHeader>
              <CardTitle className="text-xl text-gray-800">{t.budgetAllocated}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-bold text-blue-600" data-testid="budget-allocated">
                {formatNumber(currentData?.budget_allocated)}
              </p>
            </CardContent>
          </Card>

          <Card className="bg-white shadow-xl border-0">
            <CardHeader>
              <CardTitle className="text-xl text-gray-800">{t.budgetSpent}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-bold text-green-600" data-testid="budget-spent">
                {formatNumber(currentData?.budget_spent)}
              </p>
              <div className="mt-4">
                <div className="bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-green-500 to-green-600 h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${Math.min(((currentData?.budget_spent || 0) / (currentData?.budget_allocated || 1)) * 100, 100)}%`
                    }}
                  />
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {((currentData?.budget_spent || 0) / (currentData?.budget_allocated || 1) * 100).toFixed(1)}% utilized
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Historical Trend */}
        {historicalData.length > 0 && (
          <Card className="bg-white shadow-xl border-0 mb-8">
            <CardHeader>
              <CardTitle className="text-xl text-gray-800">{t.historicalTrend}</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={historicalData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                  <XAxis
                    dataKey="month"
                    tickFormatter={(val) => `${val}/${historicalData[0]?.year}`}
                    stroke="#666"
                  />
                  <YAxis stroke="#666" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(255, 255, 255, 0.95)',
                      border: '1px solid #ddd',
                      borderRadius: '8px',
                      padding: '12px'
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="total_workers"
                    stroke="#3b82f6"
                    strokeWidth={3}
                    name="Total Workers"
                    dot={{ fill: '#3b82f6', r: 5 }}
                    activeDot={{ r: 8 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="work_completed"
                    stroke="#22c55e"
                    strokeWidth={3}
                    name="Work Completed"
                    dot={{ fill: '#22c55e', r: 5 }}
                    activeDot={{ r: 8 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="person_days_generated"
                    stroke="#f97316"
                    strokeWidth={3}
                    name="Person Days"
                    dot={{ fill: '#f97316', r: 5 }}
                    activeDot={{ r: 8 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* Budget Comparison Chart */}
        {historicalData.length > 0 && (
          <Card className="bg-white shadow-xl border-0">
            <CardHeader>
              <CardTitle className="text-xl text-gray-800">Budget Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={historicalData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                  <XAxis
                    dataKey="month"
                    tickFormatter={(val) => `${val}/${historicalData[0]?.year}`}
                    stroke="#666"
                  />
                  <YAxis stroke="#666" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(255, 255, 255, 0.95)',
                      border: '1px solid #ddd',
                      borderRadius: '8px',
                      padding: '12px'
                    }}
                    formatter={(value) => formatNumber(value)}
                  />
                  <Legend />
                  <Bar dataKey="budget_allocated" fill="#3b82f6" name="Allocated" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="budget_spent" fill="#22c55e" name="Spent" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}
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

export default DistrictDetail;