import React from 'react';
import styled from 'styled-components';

const DashboardContainer = styled.div`
  padding: 20px;
  text-align: center;
`;

const Title = styled.h1`
  color: #00D4AA;
  margin-bottom: 20px;
  font-size: 32px;
`;

const Message = styled.p`
  color: #A0AEC0;
  font-size: 18px;
  margin-bottom: 10px;
`;

const StatusCard = styled.div`
  background: linear-gradient(135deg, #1A1F3A 0%, #2D3748 100%);
  border-radius: 12px;
  padding: 24px;
  margin: 20px 0;
  border: 1px solid #2D3748;
`;

const StatusTitle = styled.h3`
  color: #00D4AA;
  margin-bottom: 10px;
`;

const StatusText = styled.p`
  color: #FFFFFF;
`;

const Dashboard = () => {
  return (
    <DashboardContainer>
      <Title>Premier League Predictor Dashboard</Title>
      <Message>Welcome to the Premier League Match Predictor!</Message>
      
      <StatusCard>
        <StatusTitle>Backend Status</StatusTitle>
        <StatusText>✅ Backend API is running at http://localhost:8000</StatusText>
      </StatusCard>
      
      <StatusCard>
        <StatusTitle>Frontend Status</StatusTitle>
        <StatusText>✅ React frontend is running at http://localhost:3000</StatusText>
      </StatusCard>
      
      <StatusCard>
        <StatusTitle>API Documentation</StatusTitle>
        <StatusText>📖 Visit http://localhost:8000/docs for interactive API docs</StatusText>
      </StatusCard>
      
      <Message>🎉 Your Premier League Predictor is ready to use!</Message>
    </DashboardContainer>
  );
};

export default Dashboard;