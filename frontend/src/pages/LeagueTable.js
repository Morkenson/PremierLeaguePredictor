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

const LeagueTable = () => {
  return (
    <ComponentContainer>
      <Title>League Table</Title>
      <Message>Premier League standings and form analysis coming soon...</Message>
      <Message>Data will be fetched from the backend API!</Message>
    </ComponentContainer>
  );
};

export default LeagueTable;