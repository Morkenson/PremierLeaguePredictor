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

const Predictor = () => {
  return (
    <ComponentContainer>
      <Title>Match Predictor</Title>
      <Message>AI-powered match prediction interface coming soon...</Message>
      <Message>Backend API is ready for predictions!</Message>
    </ComponentContainer>
  );
};

export default Predictor;