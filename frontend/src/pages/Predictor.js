import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { apiService } from '../services/api';

const PredictorContainer = styled.div`
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
`;

const Title = styled.h2`
  color: #00D4AA;
  margin-bottom: 30px;
  font-size: 32px;
  text-align: center;
`;

const FormCard = styled.div`
  background: linear-gradient(135deg, #1A1F3A 0%, #2D3748 100%);
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  border: 1px solid #2D3748;
`;

const FormRow = styled.div`
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  align-items: flex-end;

  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const FormGroup = styled.div`
  flex: 1;
`;

const Label = styled.label`
  display: block;
  color: #FFFFFF;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
`;

const Select = styled.select`
  width: 100%;
  padding: 12px 16px;
  background: #0A0E27;
  border: 1px solid #2D3748;
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: #00D4AA;
  }

  &:hover {
    border-color: #00D4AA;
  }

  option {
    background: #0A0E27;
    color: #FFFFFF;
  }
`;

const Button = styled.button`
  padding: 12px 32px;
  background: linear-gradient(135deg, #00D4AA 0%, #00B894 100%);
  border: none;
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 212, 170, 0.3);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const PredictionCard = styled.div`
  background: linear-gradient(135deg, #1A1F3A 0%, #2D3748 100%);
  border-radius: 12px;
  padding: 30px;
  border: 1px solid #2D3748;
  animation: fadeIn 0.3s ease;
`;

const MatchTitle = styled.h3`
  color: #00D4AA;
  font-size: 24px;
  margin-bottom: 20px;
  text-align: center;
`;

const ScoreDisplay = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin: 30px 0;
  font-size: 48px;
  font-weight: 700;
  color: #FFFFFF;
`;

const TeamName = styled.div`
  font-size: 20px;
  color: #FFFFFF;
  text-align: center;
`;

const ProbabilitySection = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin: 30px 0;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ProbabilityCard = styled.div`
  background: #0A0E27;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  border: 1px solid #2D3748;
`;

const ProbabilityLabel = styled.div`
  color: #A0AEC0;
  font-size: 14px;
  margin-bottom: 8px;
`;

const ProbabilityValue = styled.div`
  color: #00D4AA;
  font-size: 32px;
  font-weight: 700;
`;

const ConfidenceBar = styled.div`
  background: #0A0E27;
  border-radius: 8px;
  padding: 15px;
  margin: 20px 0;
  border: 1px solid #2D3748;
`;

const ConfidenceLabel = styled.div`
  color: #A0AEC0;
  font-size: 14px;
  margin-bottom: 8px;
`;

const ConfidenceValue = styled.div`
  color: #00D4AA;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 10px;
`;

const Bar = styled.div`
  background: #2D3748;
  border-radius: 4px;
  height: 8px;
  overflow: hidden;
`;

const BarFill = styled.div`
  background: linear-gradient(90deg, #00D4AA 0%, #00B894 100%);
  height: 100%;
  width: ${props => props.width}%;
  transition: width 0.3s ease;
`;

const KeyFactors = styled.div`
  margin-top: 30px;
`;

const KeyFactorsTitle = styled.h4`
  color: #00D4AA;
  font-size: 18px;
  margin-bottom: 15px;
`;

const FactorItem = styled.div`
  background: #0A0E27;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 10px;
  border-left: 3px solid #00D4AA;
  color: #FFFFFF;
  font-size: 14px;
`;

const ErrorMessage = styled.div`
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  padding: 16px;
  color: #FCA5A5;
  margin-bottom: 20px;
  text-align: center;
`;

const LoadingMessage = styled.div`
  text-align: center;
  color: #00D4AA;
  font-size: 18px;
  padding: 40px;
`;

const VS = styled.div`
  color: #A0AEC0;
  font-size: 24px;
`;

const Predictor = () => {
  const [teams, setTeams] = useState([]);
  const [homeTeam, setHomeTeam] = useState('');
  const [awayTeam, setAwayTeam] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [loadingTeams, setLoadingTeams] = useState(true);

  useEffect(() => {
    loadTeams();
  }, []);

  const loadTeams = async () => {
    try {
      setLoadingTeams(true);
      const teamList = await apiService.getTeams();
      setTeams(teamList);
      setError(null);
    } catch (error) {
      console.error('Failed to load teams:', error);
      setError('Failed to load teams. Please check if the backend is running.');
    } finally {
      setLoadingTeams(false);
    }
  };

  const handlePredict = async () => {
    if (!homeTeam || !awayTeam) {
      setError('Please select both teams');
      return;
    }

    if (homeTeam === awayTeam) {
      setError('Please select different teams');
      return;
    }

    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const result = await apiService.predictMatch({
        home_team: homeTeam,
        away_team: awayTeam,
        season: '2023-24'
      });
      setPrediction(result);
    } catch (error) {
      console.error('Prediction error:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to generate prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatProbability = (prob) => {
    return `${(prob * 100).toFixed(1)}%`;
  };

  if (loadingTeams) {
    return (
      <PredictorContainer>
        <Title>Match Predictor</Title>
        <LoadingMessage>Loading teams...</LoadingMessage>
      </PredictorContainer>
    );
  }

  return (
    <PredictorContainer>
      <Title>Match Predictor</Title>
      
      <FormCard>
        {error && <ErrorMessage>{error}</ErrorMessage>}
        
        <FormRow>
          <FormGroup>
            <Label>Home Team</Label>
            <Select
              value={homeTeam}
              onChange={(e) => setHomeTeam(e.target.value)}
              disabled={loading}
            >
              <option value="">Select home team</option>
              {teams.map((team) => (
                <option key={team.id} value={team.name}>
                  {team.name}
                </option>
              ))}
            </Select>
          </FormGroup>

          <FormGroup>
            <Label>Away Team</Label>
            <Select
              value={awayTeam}
              onChange={(e) => setAwayTeam(e.target.value)}
              disabled={loading}
            >
              <option value="">Select away team</option>
              {teams.map((team) => (
                <option key={team.id} value={team.name}>
                  {team.name}
                </option>
              ))}
            </Select>
          </FormGroup>

          <Button onClick={handlePredict} disabled={loading || !homeTeam || !awayTeam}>
            {loading ? 'Predicting...' : 'Predict Match'}
          </Button>
        </FormRow>
      </FormCard>

      {prediction && (
        <PredictionCard>
          <MatchTitle>
            {prediction.home_team} vs {prediction.away_team}
          </MatchTitle>

          <ScoreDisplay>
            <div>
              <TeamName>{prediction.home_team}</TeamName>
              <div style={{ fontSize: '64px', color: '#00D4AA' }}>
                {prediction.predicted_score.home}
              </div>
            </div>
            <VS>VS</VS>
            <div>
              <TeamName>{prediction.away_team}</TeamName>
              <div style={{ fontSize: '64px', color: '#00D4AA' }}>
                {prediction.predicted_score.away}
              </div>
            </div>
          </ScoreDisplay>

          <ProbabilitySection>
            <ProbabilityCard>
              <ProbabilityLabel>Home Win</ProbabilityLabel>
              <ProbabilityValue>
                {formatProbability(prediction.home_win_probability)}
              </ProbabilityValue>
            </ProbabilityCard>
            <ProbabilityCard>
              <ProbabilityLabel>Draw</ProbabilityLabel>
              <ProbabilityValue>
                {formatProbability(prediction.draw_probability)}
              </ProbabilityValue>
            </ProbabilityCard>
            <ProbabilityCard>
              <ProbabilityLabel>Away Win</ProbabilityLabel>
              <ProbabilityValue>
                {formatProbability(prediction.away_win_probability)}
              </ProbabilityValue>
            </ProbabilityCard>
          </ProbabilitySection>

          <ConfidenceBar>
            <ConfidenceLabel>Prediction Confidence</ConfidenceLabel>
            <ConfidenceValue>{formatProbability(prediction.confidence)}</ConfidenceValue>
            <Bar>
              <BarFill width={prediction.confidence * 100} />
            </Bar>
          </ConfidenceBar>

          {prediction.key_factors && prediction.key_factors.length > 0 && (
            <KeyFactors>
              <KeyFactorsTitle>Key Factors</KeyFactorsTitle>
              {prediction.key_factors.map((factor, index) => (
                <FactorItem key={index}>{factor}</FactorItem>
              ))}
            </KeyFactors>
          )}
        </PredictionCard>
      )}
    </PredictorContainer>
  );
};

export default Predictor;
