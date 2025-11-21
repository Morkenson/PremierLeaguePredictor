import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Trophy, TrendingUp, BarChart3, Home, Plane, Loader } from 'lucide-react';
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

const SelectContainer = styled.div`
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const Select = styled.select`
  width: 100%;
  max-width: 400px;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.medium};
  color: ${props => props.theme.colors.text};
  font-size: ${props => props.theme.typography.fontSize.base};
  cursor: pointer;
  transition: all ${props => props.theme.transitions.normal};

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.primaryGlow};
  }

  option {
    background: ${props => props.theme.colors.surface};
    color: ${props => props.theme.colors.text};
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const StatCard = styled(motion.div)`
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

const StatHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const StatIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: ${props => props.theme.borderRadius.medium};
  background: ${props => props.iconBg || props.theme.gradients.primarySubtle};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.iconColor || props.theme.colors.primary};
  flex-shrink: 0;
`;

const StatTitle = styled.h3`
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const StatValue = styled.div`
  font-size: ${props => props.theme.typography.fontSize['4xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const StatLabel = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.textSecondary};
`;

const RecordGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-top: ${props => props.theme.spacing.xl};
`;

const RecordCard = styled(motion.div)`
  background: ${props => props.theme.gradients.card};
  backdrop-filter: blur(10px);
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.small};
`;

const RecordTitle = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: ${props => props.theme.spacing.md};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const RecordStats = styled.div`
  display: flex;
  justify-content: space-around;
  gap: ${props => props.theme.spacing.md};
`;

const RecordStat = styled.div`
  text-align: center;
`;

const RecordStatValue = styled.div`
  font-size: ${props => props.theme.typography.fontSize['2xl']};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  color: ${props => props.theme.colors.text};
`;

const RecordStatLabel = styled.div`
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.textSecondary};
  margin-top: ${props => props.theme.spacing.xs};
`;

const FormIndicator = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.xs};
  margin-top: ${props => props.theme.spacing.md};
  flex-wrap: wrap;
`;

const FormBadge = styled.div`
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.small};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  background: ${props => {
    if (props.result === 'W') return 'rgba(16, 185, 129, 0.2)';
    if (props.result === 'D') return 'rgba(245, 158, 11, 0.2)';
    return 'rgba(239, 68, 68, 0.2)';
  }};
  color: ${props => {
    if (props.result === 'W') return props.theme.colors.success;
    if (props.result === 'D') return props.theme.colors.warning;
    return props.theme.colors.error;
  }};
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

const TeamStats = () => {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingTeams, setLoadingTeams] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadTeams();
  }, []);

  useEffect(() => {
    if (selectedTeam) {
      loadTeamStats(selectedTeam);
    }
  }, [selectedTeam]);

  const loadTeams = async () => {
    try {
      setLoadingTeams(true);
      const teamList = await apiService.getTeams();
      setTeams(teamList);
      if (teamList.length > 0) {
        setSelectedTeam(teamList[0].name);
      }
    } catch (error) {
      console.error('Failed to load teams:', error);
      setError('Failed to load teams. Please check if the backend is running.');
      toast.error('Failed to load teams');
    } finally {
      setLoadingTeams(false);
    }
  };

  const loadTeamStats = async (teamName) => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getTeamStats(teamName);
      setStats(data);
    } catch (error) {
      console.error('Failed to load team stats:', error);
      setError('Failed to load team statistics. Please try again.');
      toast.error('Failed to load team statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loadingTeams) {
    return (
      <PageContainer>
        <LoadingContainer>
          <LoadingSpinner size={48} />
          <p style={{ marginTop: '16px' }}>Loading teams...</p>
        </LoadingContainer>
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
          <PageTitle>Team Statistics</PageTitle>
          <PageSubtitle>
            Detailed performance analysis for Premier League teams
          </PageSubtitle>
        </HeaderSection>

        <SelectContainer>
          <Select
            value={selectedTeam}
            onChange={(e) => setSelectedTeam(e.target.value)}
            disabled={loading}
          >
            {teams.map((team) => (
              <option key={team.id} value={team.name}>
                {team.name}
              </option>
            ))}
          </Select>
        </SelectContainer>

        {error && <ErrorMessage>{error}</ErrorMessage>}

        {loading && (
          <LoadingContainer>
            <LoadingSpinner size={48} />
            <p style={{ marginTop: '16px' }}>Loading statistics...</p>
          </LoadingContainer>
        )}

        {stats && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <StatsGrid>
              <StatCard whileHover={{ scale: 1.02 }}>
                <StatHeader>
                  <StatIcon iconBg="rgba(16, 185, 129, 0.1)" iconColor="#10B981">
                    <Trophy size={24} />
                  </StatIcon>
                  <StatTitle>Points</StatTitle>
                </StatHeader>
                <StatValue>{stats.points}</StatValue>
                <StatLabel>Total points this season</StatLabel>
              </StatCard>

              <StatCard whileHover={{ scale: 1.02 }}>
                <StatHeader>
                  <StatIcon iconBg="rgba(6, 182, 212, 0.1)" iconColor="#06B6D4">
                    <BarChart3 size={24} />
                  </StatIcon>
                  <StatTitle>Matches Played</StatTitle>
                </StatHeader>
                <StatValue>{stats.wins + stats.draws + stats.losses}</StatValue>
                <StatLabel>
                  {stats.wins}W / {stats.draws}D / {stats.losses}L
                </StatLabel>
              </StatCard>

              <StatCard whileHover={{ scale: 1.02 }}>
                <StatHeader>
                  <StatIcon iconBg="rgba(139, 92, 246, 0.1)" iconColor="#8B5CF6">
                    <TrendingUp size={24} />
                  </StatIcon>
                  <StatTitle>Goals</StatTitle>
                </StatHeader>
                <StatValue>{stats.goals_for}</StatValue>
                <StatLabel>
                  {stats.goals_for} for / {stats.goals_against} against
                </StatLabel>
              </StatCard>
            </StatsGrid>

            <RecordGrid>
              <RecordCard
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <RecordTitle>
                  <Home size={16} />
                  Home Record
                </RecordTitle>
                <RecordStats>
                  <RecordStat>
                    <RecordStatValue>{stats.home_record.wins}</RecordStatValue>
                    <RecordStatLabel>Wins</RecordStatLabel>
                  </RecordStat>
                  <RecordStat>
                    <RecordStatValue>{stats.home_record.draws}</RecordStatValue>
                    <RecordStatLabel>Draws</RecordStatLabel>
                  </RecordStat>
                  <RecordStat>
                    <RecordStatValue>{stats.home_record.losses}</RecordStatValue>
                    <RecordStatLabel>Losses</RecordStatLabel>
                  </RecordStat>
                </RecordStats>
              </RecordCard>

              <RecordCard
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <RecordTitle>
                  <Plane size={16} />
                  Away Record
                </RecordTitle>
                <RecordStats>
                  <RecordStat>
                    <RecordStatValue>{stats.away_record.wins}</RecordStatValue>
                    <RecordStatLabel>Wins</RecordStatLabel>
                  </RecordStat>
                  <RecordStat>
                    <RecordStatValue>{stats.away_record.draws}</RecordStatValue>
                    <RecordStatLabel>Draws</RecordStatLabel>
                  </RecordStat>
                  <RecordStat>
                    <RecordStatValue>{stats.away_record.losses}</RecordStatValue>
                    <RecordStatLabel>Losses</RecordStatLabel>
                  </RecordStat>
                </RecordStats>
              </RecordCard>
            </RecordGrid>

            {stats.form && stats.form.length > 0 && (
              <StatCard
                style={{ marginTop: '24px' }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <StatTitle style={{ marginBottom: '16px' }}>Recent Form</StatTitle>
                <FormIndicator>
                  {stats.form.map((result, index) => (
                    <FormBadge key={index} result={result}>
                      {result}
                    </FormBadge>
                  ))}
                </FormIndicator>
              </StatCard>
            )}
          </motion.div>
        )}
      </motion.div>
    </PageContainer>
  );
};

export default TeamStats;
