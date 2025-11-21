import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Calendar, Clock, Target, Loader } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const PageContainer = styled.div`
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
`;

const HeaderSection = styled(motion.div)`
  margin-bottom: ${props => props.theme.spacing['2xl']};
`;

const PageTitle = styled.h1`
  font-size: ${props => props.theme.typography.fontSize['4xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  color: ${props => props.theme.colors.text};
  margin: 0 0 ${props => props.theme.spacing.sm} 0;
  line-height: ${props => props.theme.typography.lineHeight.tight};
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    font-size: ${props => props.theme.typography.fontSize['3xl']};
  }
`;

const PageSubtitle = styled.p`
  font-size: ${props => props.theme.typography.fontSize.lg};
  color: ${props => props.theme.colors.textSecondary};
  margin: 0;
  line-height: ${props => props.theme.typography.lineHeight.normal};
`;

const FixturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  
  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    grid-template-columns: 1fr;
  }
`;

const FixtureCard = styled(motion.div)`
  background: ${props => props.theme.gradients.card};
  backdrop-filter: blur(10px);
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.small};
  transition: all ${props => props.theme.transitions.normal};
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.medium};
    border-color: ${props => props.theme.colors.primary};
  }
`;

const FixtureHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.lg};
  padding-bottom: ${props => props.theme.spacing.md};
  border-bottom: 1px solid ${props => props.theme.colors.borderLight};
`;

const FixtureDate = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.textSecondary};
`;

const FixtureStatus = styled.div`
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.small};
  font-size: ${props => props.theme.typography.fontSize.xs};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  background: ${props => {
    if (props.status === 'FINISHED') return 'rgba(16, 185, 129, 0.2)';
    if (props.status === 'LIVE') return 'rgba(239, 68, 68, 0.2)';
    return 'rgba(6, 182, 212, 0.2)';
  }};
  color: ${props => {
    if (props.status === 'FINISHED') return props.theme.colors.success;
    if (props.status === 'LIVE') return props.theme.colors.error;
    return props.theme.colors.primary;
  }};
`;

const TeamsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const TeamRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const TeamName = styled.div`
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  color: ${props => props.theme.colors.text};
  flex: 1;
`;

const Score = styled.div`
  font-size: ${props => props.theme.typography.fontSize['2xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  color: ${props => props.theme.colors.primary};
  min-width: 60px;
  text-align: center;
`;

const VS = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.textMuted};
  text-align: center;
  margin: ${props => props.theme.spacing.sm} 0;
`;

const PredictionBadge = styled.div`
  margin-top: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background: ${props => props.theme.gradients.primarySubtle};
  border: 1px solid ${props => props.theme.colors.primary};
  border-radius: ${props => props.theme.borderRadius.medium};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.primary};
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing['3xl']};
  color: ${props => props.theme.colors.textSecondary};
`;

const LoadingSpinner = styled(Loader)`
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: ${props => props.theme.borderRadius.large};
  padding: ${props => props.theme.spacing.xl};
  text-align: center;
  color: #FCA5A5;
  margin: ${props => props.theme.spacing.xl} 0;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing['3xl']};
  color: ${props => props.theme.colors.textSecondary};
`;

const Fixtures = () => {
  const [fixtures, setFixtures] = useState([]);
  const [predictions, setPredictions] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadFixtures();
    loadPredictions();
  }, []);

  const loadFixtures = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getUpcomingFixtures();
      setFixtures(data);
    } catch (error) {
      console.error('Failed to load fixtures:', error);
      setError('Failed to load fixtures. Please try again.');
      toast.error('Failed to load fixtures');
    } finally {
      setLoading(false);
    }
  };

  const loadPredictions = async () => {
    try {
      const data = await apiService.getBatchPredictions();
      const predictionsMap = {};
      data.forEach((pred) => {
        const key = `${pred.home_team}_${pred.away_team}`;
        predictionsMap[key] = pred;
      });
      setPredictions(predictionsMap);
    } catch (error) {
      console.error('Failed to load predictions:', error);
      // Don't show error for predictions, they're optional
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'TBD';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getPrediction = (homeTeam, awayTeam) => {
    const key = `${homeTeam}_${awayTeam}`;
    return predictions[key];
  };

  if (loading) {
    return (
      <PageContainer>
        <LoadingContainer>
          <LoadingSpinner size={48} />
          <p style={{ marginTop: '16px' }}>Loading fixtures...</p>
        </LoadingContainer>
      </PageContainer>
    );
  }

  if (error) {
    return (
      <PageContainer>
        <ErrorMessage>{error}</ErrorMessage>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <HeaderSection>
          <PageTitle>Upcoming Fixtures</PageTitle>
          <PageSubtitle>
            Premier League matches with AI-powered predictions
          </PageSubtitle>
        </HeaderSection>

        {fixtures.length === 0 ? (
          <EmptyState>
            <Calendar size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
            <p>No upcoming fixtures available at the moment.</p>
          </EmptyState>
        ) : (
          <FixturesGrid>
            {fixtures.map((fixture, index) => {
              const prediction = getPrediction(fixture.home_team, fixture.away_team);
              return (
                <FixtureCard
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  whileHover={{ scale: 1.02 }}
                >
                  <FixtureHeader>
                    <FixtureDate>
                      <Clock size={16} />
                      {formatDate(fixture.date)}
                    </FixtureDate>
                    <FixtureStatus status={fixture.status}>
                      {fixture.status}
                    </FixtureStatus>
                  </FixtureHeader>

                  <TeamsContainer>
                    <TeamRow>
                      <TeamName>{fixture.home_team}</TeamName>
                      {fixture.score && (
                        <Score>{fixture.score.home || '-'}</Score>
                      )}
                    </TeamRow>
                    <VS>VS</VS>
                    <TeamRow>
                      <TeamName>{fixture.away_team}</TeamName>
                      {fixture.score && (
                        <Score>{fixture.score.away || '-'}</Score>
                      )}
                    </TeamRow>
                  </TeamsContainer>

                  {prediction && (
                    <PredictionBadge>
                      <Target size={16} />
                      Prediction: {prediction.home_team} {Math.round(prediction.home_win_probability * 100)}% | 
                      Draw {Math.round(prediction.draw_probability * 100)}% | 
                      {prediction.away_team} {Math.round(prediction.away_win_probability * 100)}%
                    </PredictionBadge>
                  )}
                </FixtureCard>
              );
            })}
          </FixturesGrid>
        )}
      </motion.div>
    </PageContainer>
  );
};

export default Fixtures;
