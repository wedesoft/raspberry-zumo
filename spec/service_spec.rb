require_relative '../service'


describe Service do
  let(:udp_server) { double 'udp_server' }
  let(:gpio) { double 'gpio' }

  before :each do
    allow(GPIO).to receive(:new).and_return gpio
    allow(UDPServer).to receive(:new).and_return udp_server
  end

  describe :initialize do
    it 'should initialize general purpose input/output' do
      expect(GPIO).to receive :new
      Service.new
    end

    it 'should initialize the UDP server' do
      expect(UDPServer).to receive :new
      Service.new
    end
  end

  describe :update do
    it 'should receive UDP packets' do
      expect(udp_server).to receive :read
      Service.new.update
    end
  end
end
