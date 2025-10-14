import React from 'react';
import styled from 'styled-components';

const ComponentContainer = styled.div`
  padding: 20px;
  text-align: center;
`;

const Title = styled.h2`
  color: #00D4AA;
  margin-bottom: 20px;
  font-size: 28px;
`;

const Message = styled.p`
  color: #A0AEC0;
  font-size: 16px;
`;

const TeamStats = () => {
  return (
    <ComponentContainer>
      <Title>Team Statistics</Title>
      <Message>Detailed team performance analysis coming soon...</Message>
      <Message>Statistics will be powered by ML models!</Message>
    </ComponentContainer>
  );
};

export default TeamStats;