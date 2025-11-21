import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Trophy, TrendingUp, TrendingDown, Minus, Loader } from 'lucide-react';
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

const TableContainer = styled(motion.div)`
  background: ${props => props.theme.gradients.card};
  backdrop-filter: blur(10px);
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.large};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.small};
  overflow-x: auto;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.thead`
  background: ${props => props.theme.colors.surface};
  border-bottom: 2px solid ${props => props.theme.colors.border};
`;

const TableHeaderRow = styled.tr``;

const TableHeaderCell = styled.th`
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.sm};
  text-align: ${props => props.align || 'left'};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  color: ${props => props.theme.colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  
  &:first-child {
    padding-left: ${props => props.theme.spacing.lg};
  }
  
  &:last-child {
    padding-right: ${props => props.theme.spacing.lg};
  }
`;

const TableBody = styled.tbody``;

const TableRow = styled(motion.tr)`
  border-bottom: 1px solid ${props => props.theme.colors.borderLight};
  transition: all ${props => props.theme.transitions.normal};
  
  &:hover {
    background: ${props => props.theme.colors.surfaceHover};
  }
  
  &:last-child {
    border-bottom: none;
  }
`;

const TableCell = styled.td`
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.sm};
  font-size: ${props => props.theme.typography.fontSize.base};
  color: ${props => props.theme.colors.text};
  text-align: ${props => props.align || 'left'};
  
  &:first-child {
    padding-left: ${props => props.theme.spacing.lg};
  }
  
  &:last-child {
    padding-right: ${props => props.theme.spacing.lg};
  }
`;

const PositionCell = styled(TableCell)`
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  font-size: ${props => props.theme.typography.fontSize.lg};
  color: ${props => {
    if (props.position <= 4) return props.theme.colors.success; // Champions League
    if (props.position <= 6) return props.theme.colors.info; // Europa League
    if (props.position >= 18) return props.theme.colors.error; // Relegation
    return props.theme.colors.text;
  }};
`;

const TeamNameCell = styled(TableCell)`
  font-weight: ${props => props.theme.typography.fontWeight.semibold};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const FormIndicator = styled.div`
  display: flex;
  gap: 2px;
  margin-left: ${props => props.theme.spacing.sm};
`;

const FormDot = styled.div`
  width: 6px;
  height: 6px;
  border-radius: ${props => props.theme.borderRadius.full};
  background: ${props => {
    if (props.result === 'W') return props.theme.colors.success;
    if (props.result === 'D') return props.theme.colors.warning;
    return props.theme.colors.error;
  }};
`;

const StatCell = styled(TableCell)`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  color: ${props => props.theme.colors.textSecondary};
`;

const PointsCell = styled(TableCell)`
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  font-size: ${props => props.theme.typography.fontSize.lg};
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

const LeagueTable = () => {
  const [table, setTable] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadLeagueTable();
  }, []);

  const loadLeagueTable = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getLeagueTable();
      setTable(data);
    } catch (error) {
      console.error('Failed to load league table:', error);
      setError('Failed to load league table. Please try again.');
      toast.error('Failed to load league table');
    } finally {
      setLoading(false);
    }
  };

  const renderForm = (formString) => {
    if (!formString || formString.length === 0) return null;
    return (
      <FormIndicator>
        {formString.split('').slice(0, 5).map((result, index) => (
          <FormDot key={index} result={result} />
        ))}
      </FormIndicator>
    );
  };

  if (loading) {
    return (
      <PageContainer>
        <LoadingContainer>
          <LoadingSpinner size={48} />
          <p style={{ marginTop: '16px' }}>Loading league table...</p>
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
          <PageTitle>League Table</PageTitle>
          <PageSubtitle>
            Current Premier League standings and team form
          </PageSubtitle>
        </HeaderSection>

        <TableContainer
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Table>
            <TableHeader>
              <TableHeaderRow>
                <TableHeaderCell style={{ width: '60px' }}>Pos</TableHeaderCell>
                <TableHeaderCell>Team</TableHeaderCell>
                <TableHeaderCell align="center">P</TableHeaderCell>
                <TableHeaderCell align="center">W</TableHeaderCell>
                <TableHeaderCell align="center">D</TableHeaderCell>
                <TableHeaderCell align="center">L</TableHeaderCell>
                <TableHeaderCell align="center">GF</TableHeaderCell>
                <TableHeaderCell align="center">GA</TableHeaderCell>
                <TableHeaderCell align="center">GD</TableHeaderCell>
                <TableHeaderCell align="center">Pts</TableHeaderCell>
              </TableHeaderRow>
            </TableHeader>
            <TableBody>
              {table.map((team, index) => (
                <TableRow
                  key={team.team_name || index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.02 }}
                >
                  <PositionCell position={team.position}>
                    {team.position}
                  </PositionCell>
                  <TeamNameCell>
                    {team.team_name}
                    {team.form && renderForm(team.form)}
                  </TeamNameCell>
                  <StatCell align="center">{team.played || 0}</StatCell>
                  <StatCell align="center">{team.wins || 0}</StatCell>
                  <StatCell align="center">{team.draws || 0}</StatCell>
                  <StatCell align="center">{team.losses || 0}</StatCell>
                  <StatCell align="center">{team.goals_for || 0}</StatCell>
                  <StatCell align="center">{team.goals_against || 0}</StatCell>
                  <StatCell align="center">
                    {team.goal_difference > 0 ? '+' : ''}{team.goal_difference || 0}
                  </StatCell>
                  <PointsCell align="center">{team.points || 0}</PointsCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </motion.div>
    </PageContainer>
  );
};

export default LeagueTable;
